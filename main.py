# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Solicitudes de Ayuda — Cliente Windows/Linux/macOS
Punto de entrada principal.
"""
import json
import os
import platform
import socket
import threading
import time

import config as cfg
from core import alert, network
from platform_support import hotkey
DRILL_HOTKEY = "<ctrl>+<shift>+<f12>"
from platform_support import autostart, trigger_socket, wayland_shortcuts
from ui import alert_popup, help_window, hotkey_info, setup_window, tray

# Estado global de la aplicación
_app_cfg: dict = {}
_tray: tray.TrayIcon | None = None
_send_enabled = False


# ─── Listener UDP ──────────────────────────────────────────────────────────────

def _start_udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", cfg.UDP_PORT))
    except OSError:
        return  # Puerto en uso — otro cliente ya está escuchando

    def loop():
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                msg = json.loads(data.decode())
                alert.on_udp_message(msg, addr[0], _app_cfg)
            except Exception:
                pass

    threading.Thread(target=loop, daemon=True, name="udp-listener").start()


# ─── Heartbeat ─────────────────────────────────────────────────────────────────

def _heartbeat_loop():
    while True:
        time.sleep(cfg.HEARTBEAT_INTERVAL)
        server_ip = _app_cfg.get("server_ip")
        client_id = _app_cfg.get("client_id", "")

        network.send_heartbeat_udp(client_id)

        if server_ip:
            peers = network.heartbeat(server_ip, client_id)
            if peers is not None:
                _app_cfg["peers"] = peers
                cfg.save(_app_cfg)
            else:
                # Servidor perdido
                _app_cfg["server_ip"] = None
                _update_tray_status()

        # Reintenta descubrir servidor si no hay
        if not _app_cfg.get("server_ip"):
            manual_url = _app_cfg.get("server_url", "")
            if manual_url:
                _on_server_found(manual_url)
            else:
                found = network.discover_server(timeout=2)
                if found:
                    _on_server_found(found)


def _update_tray_status():
    if _tray:
        _tray.set_status(
            has_location=cfg.is_location_complete(_app_cfg),
            has_server=bool(_app_cfg.get("server_ip")),
        )


# ─── Conexión con el servidor ──────────────────────────────────────────────────

def _fetch_hotkey(server_ip: str):
    server_cfg = network.get_server_config(server_ip)
    hotkey_display = server_cfg.get("hotkey", cfg.DEFAULT_HOTKEY_DISPLAY)
    if hotkey_display != _app_cfg.get("hotkey_display"):
        _app_cfg["hotkey_display"] = hotkey_display
        _app_cfg["hotkey"]         = cfg.human_to_pynput(hotkey_display)
        cfg.save(_app_cfg)
        _register_hotkey()


def _on_server_found(server_ip: str):
    _app_cfg["server_ip"] = server_ip
    client_id = _app_cfg["client_id"]

    _fetch_hotkey(server_ip)

    result = network.register(server_ip, client_id, socket.gethostname())
    if result:
        _app_cfg["group_id"]    = result.get("group_id")
        _app_cfg["is_security"] = result.get("is_security", False)
        _app_cfg["peers"]       = result.get("peers", [])
        loc = result.get("location", {})
        if loc.get("room"):
            _app_cfg.update({
                "room":     loc["room"],
                "floor":    loc["floor"],
                "building": loc["building"],
                "center":   loc["center"],
            })
        room_id = result.get("room_id")
        if room_id:
            _app_cfg["room_id"] = room_id
        cfg.save(_app_cfg)
    _update_tray_status()


# ─── Hotkey ────────────────────────────────────────────────────────────────────

def _on_hotkey():
    if not _send_enabled:
        return
    alert.send_alert(_app_cfg)


def _on_drill_hotkey():
    if not _send_enabled:
        return
    alert.send_drill_alert(_app_cfg)


def _register_hotkey():
    hotkey.register("alert", _app_cfg.get("hotkey", cfg.DEFAULT_HOTKEY), _on_hotkey)
    hotkey.register("drill", DRILL_HOTKEY, _on_drill_hotkey)


# ─── Flujo de configuración de ubicación ──────────────────────────────────────

def _open_setup():
    global _send_enabled

    def on_confirm(updates: dict):
        global _send_enabled
        new_server_url = updates.pop("server_url", None)
        _app_cfg.update(updates)
        if new_server_url is not None:
            _app_cfg["server_url"] = new_server_url
            # Si la URL manual cambió, descartamos el server_ip actual para reconectar
            if new_server_url != _app_cfg.get("server_ip", ""):
                _app_cfg["server_ip"] = new_server_url if new_server_url else None
        cfg.save(_app_cfg)
        _send_enabled = cfg.is_location_complete(_app_cfg)
        _update_tray_status()
        if _tray:
            _tray.update_location(_app_cfg.get("room", ""))
        _register_hotkey()

    def on_skip():
        global _send_enabled
        _send_enabled = False
        _update_tray_status()
        _register_hotkey()

    win = setup_window.SetupWindow(_app_cfg, on_confirm=on_confirm, on_skip=on_skip)
    win.run()


# ─── Arranque ──────────────────────────────────────────────────────────────────

def _is_wayland() -> bool:
    if platform.system() != "Linux":
        return False
    return (os.environ.get("XDG_SESSION_TYPE") == "wayland"
            or bool(os.environ.get("WAYLAND_DISPLAY")))


def _setup_wayland_shortcuts():
    """
    En Wayland, pynput no puede capturar hotkeys globales.
    Configuramos atajos en el entorno de ventanas (GNOME/KDE) que llaman
    al propio ejecutable con --trigger o --drill.
    """
    import tkinter as tk
    from tkinter import messagebox

    hotkey_display = _app_cfg.get("hotkey_display", cfg.DEFAULT_HOTKEY_DISPLAY)
    de = wayland_shortcuts.detect_desktop()

    root = tk.Tk()
    root.withdraw()

    if de == "unknown":
        messagebox.showwarning(
            "Wayland — Configuración manual necesaria",
            "Se ha detectado una sesión Wayland en un entorno de escritorio\n"
            "no reconocido (ni GNOME ni KDE).\n\n"
            "Los atajos de teclado globales no funcionarán automáticamente.\n\n"
            "Configura manualmente un atajo de teclado en tu entorno que ejecute:\n\n"
            f"  Para alertas reales:  {wayland_shortcuts._executable()} --trigger\n"
            f"  Para simulacros:      {wayland_shortcuts._executable()} --drill",
        )
        root.destroy()
        return

    answer = messagebox.askyesno(
        "Wayland detectado",
        f"Se ha detectado una sesión Wayland ({de.upper()}).\n\n"
        "En Wayland los atajos de teclado globales requieren registrarse\n"
        "en el entorno de ventanas.\n\n"
        f"¿Deseas configurar automáticamente los atajos\n"
        f"  {hotkey_display}  →  alerta real\n"
        f"  Ctrl+Shift+F12  →  simulacro\n\n"
        "en tu entorno de escritorio ahora?",
    )
    root.destroy()

    if not answer:
        return

    try:
        wayland_shortcuts.setup(hotkey_display)
        root2 = tk.Tk()
        root2.withdraw()
        messagebox.showinfo(
            "Atajos configurados",
            f"Los atajos han sido registrados en {de.upper()}.\n\n"
            "Puede que necesites cerrar y volver a abrir sesión\n"
            "para que los atajos queden activos.",
        )
        root2.destroy()
    except Exception as e:
        root2 = tk.Tk()
        root2.withdraw()
        messagebox.showerror("Error al configurar atajos", str(e))
        root2.destroy()


def _handle_trigger_args() -> bool:
    """
    Si el proceso fue invocado con --trigger o --drill, reenvía el comando
    a la instancia en ejecución y termina. Devuelve True si hay que salir.
    """
    import sys
    args = sys.argv[1:]
    if "--trigger" in args:
        trigger_socket.send_trigger(trigger_socket.TRIGGER_ALERT)
        return True
    if "--drill" in args:
        trigger_socket.send_trigger(trigger_socket.TRIGGER_DRILL)
        return True
    return False


def main():
    global _app_cfg, _tray, _send_enabled

    if _handle_trigger_args():
        return

    _app_cfg = cfg.load()
    autostart.enable()

    alert.set_alert_callback(alert_popup.show)

    _start_udp_listener()

    # Socket Unix para disparos externos (Wayland / scripts / macOS shortcuts)
    if platform.system() in ("Linux", "Darwin"):
        trigger_socket.start_listener(
            on_alert=lambda: alert.send_alert(_app_cfg) if _send_enabled else None,
            on_drill=lambda: alert.send_drill_alert(_app_cfg) if _send_enabled else None,
        )

    # Descubrimiento inicial síncrono para que la ventana de configuración
    # ya tenga el servidor resuelto al abrirse.
    manual_url = _app_cfg.get("server_url", "")
    server_ip = manual_url or network.discover_server(timeout=3)
    if server_ip:
        _on_server_found(server_ip)

    threading.Thread(target=_heartbeat_loop, daemon=True, name="heartbeat").start()

    # Ventana de configuración de ubicación
    _open_setup()

    # En Wayland, ofrece configurar atajos en el entorno de ventanas
    if _is_wayland():
        _setup_wayland_shortcuts()

    # En macOS, comprueba permiso de Accesibilidad antes de registrar hotkeys
    _macos_accessibility_ok = True
    if platform.system() == "Darwin":
        from platform_support import macos_permissions
        _macos_accessibility_ok = macos_permissions.ensure_accessibility()

    _send_enabled = cfg.is_location_complete(_app_cfg)
    hotkeys_active = not _is_wayland() and _macos_accessibility_ok
    if hotkeys_active:
        _register_hotkey()

    # Ventana de información del hotkey (siempre al arrancar)
    location_text = _app_cfg.get("room") or "Sin ubicación configurada"
    hotkey_info.show(
        hotkey_display=_app_cfg.get("hotkey_display", cfg.DEFAULT_HOTKEY_DISPLAY),
        location_text=location_text,
        send_enabled=_send_enabled,
    )

    _tray = tray.TrayIcon(
        app_cfg=_app_cfg,
        on_open_config=_open_setup,
        on_help=help_window.show,
        on_quit=lambda: None,
    )
    _tray.set_status(
        has_location=_send_enabled,
        has_server=bool(_app_cfg.get("server_ip")),
    )
    _tray.run()


if __name__ == "__main__":
    main()
