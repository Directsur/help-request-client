# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import base64
import io
import json
import os
import platform
import subprocess
import sys
import threading
from PIL import Image, ImageDraw
import pystray


def _make_icon(color: str, size: int = 22) -> Image.Image:
    S = size * 4
    img  = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    m = S / 64
    draw.polygon([(32*m, 4*m), (62*m, 58*m), (2*m,  58*m)], fill=color)
    draw.polygon([(32*m, 18*m), (50*m, 50*m), (14*m, 50*m)], fill="white")
    draw.rectangle([29*m, 26*m, 35*m, 42*m], fill=color)
    draw.ellipse([29*m, 45*m, 35*m, 51*m], fill=color)
    return img.resize((size, size), Image.LANCZOS)


_ICONS = {
    "ok":          _make_icon("#27ae60"),
    "no_location": _make_icon("#f39c12"),
    "no_server":   _make_icon("#e74c3c"),
    "offline":     _make_icon("#7f8c8d"),
}


def _icon_to_png_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _find_helper() -> str | None:
    """Devuelve la ruta al helper GTK, tanto en dev como en bundle."""
    base = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "tray_gtk_helper.py")
    return path if os.path.exists(path) else None


def _is_linux_x11() -> bool:
    if platform.system() != "Linux":
        return False
    if os.environ.get("WAYLAND_DISPLAY"):
        return False
    if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
        return False
    return True


class TrayIcon:
    def __init__(self, app_cfg: dict, on_open_config, on_help, on_quit):
        self.cfg            = app_cfg
        self.on_open_config = on_open_config
        self.on_help        = on_help
        self.on_quit        = on_quit
        self._status        = "offline"
        self._proc          = None   # subproceso GTK
        self._icon          = None   # pystray fallback

    # ── estado ──────────────────────────────────────────────────────────────
    def set_status(self, has_location: bool, has_server: bool):
        if has_location and has_server:
            self._status = "ok"
        elif has_location:
            self._status = "no_server"
        elif has_server:
            self._status = "no_location"
        else:
            self._status = "offline"

        if self._proc:
            self._send({"cmd": "set_icon",    "png_b64": _icon_to_png_b64(_ICONS[self._status])})
            self._send({"cmd": "set_tooltip", "text": self._get_title()})
        elif self._icon:
            self._icon.icon  = _ICONS[self._status]
            self._icon.title = self._get_title()

    def update_location(self, room: str):
        self.cfg["room"] = room
        if self._proc:
            self._send({"cmd": "set_menu",
                        "room":   room or "Sin ubicación",
                        "hotkey": self.cfg.get("hotkey_display", "Ctrl+F12")})
        elif self._icon:
            self._icon.menu = self._build_pystray_menu()

    # ── helpers internos ────────────────────────────────────────────────────
    def _get_title(self) -> str:
        hotkey = self.cfg.get("hotkey_display", "Ctrl+F12")
        return {
            "ok":          f"Solicitudes de Ayuda | {hotkey} para pedir ayuda",
            "no_location": "Solicitudes de Ayuda | Sin ubicación (solo recepción)",
            "no_server":   f"Solicitudes de Ayuda | {hotkey} para pedir ayuda (sin servidor)",
            "offline":     "Solicitudes de Ayuda | Sin configurar",
        }.get(self._status, "Solicitudes de Ayuda")

    def _send(self, data: dict):
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.stdin.write(json.dumps(data) + "\n")
                self._proc.stdin.flush()
            except Exception:
                pass

    def _dispatch(self, action: str):
        if action == "open_config":
            threading.Thread(target=self.on_open_config, daemon=True).start()
        elif action == "help":
            threading.Thread(target=self.on_help, daemon=True).start()
        elif action == "quit":
            self._send({"cmd": "quit"})
            self.on_quit()

    # ── pystray fallback ────────────────────────────────────────────────────
    def _build_pystray_menu(self):
        location = self.cfg.get("room") or "Sin ubicación"
        hotkey   = self.cfg.get("hotkey_display", "Ctrl+F12")
        return pystray.Menu(
            pystray.MenuItem(f"📍 {location}", None, enabled=False),
            pystray.MenuItem(f"⌨  {hotkey} — solicitar ayuda", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Configurar ubicación...", lambda: self.on_open_config()),
            pystray.MenuItem("Ayuda...", lambda: self.on_help()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", lambda: self._quit_pystray()),
        )

    def _quit_pystray(self):
        if self._icon:
            self._icon.stop()
        self.on_quit()

    # ── arranque ────────────────────────────────────────────────────────────
    def run(self):
        if _is_linux_x11():
            helper = _find_helper()
            if helper:
                try:
                    self._run_subprocess(helper)
                    return
                except Exception:
                    pass

        # Fallback: pystray
        self._icon = pystray.Icon(
            name="help-request",
            icon=_ICONS.get(self._status, _ICONS["offline"]),
            title=self._get_title(),
            menu=self._build_pystray_menu(),
        )
        self._icon.run()

    def _run_subprocess(self, helper_path: str):
        self._proc = subprocess.Popen(
            ["python3", helper_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,
            text=True,
            bufsize=1,
        )

        # Estado inicial
        self._send({"cmd": "set_icon",    "png_b64": _icon_to_png_b64(_ICONS[self._status])})
        self._send({"cmd": "set_tooltip", "text": self._get_title()})
        self._send({"cmd": "set_menu",
                    "room":   self.cfg.get("room") or "Sin ubicación",
                    "hotkey": self.cfg.get("hotkey_display", "Ctrl+F12")})

        # Bucle de lectura de acciones (bloquea hasta que el helper termina)
        for line in self._proc.stdout:
            line = line.strip()
            if line:
                try:
                    msg = json.loads(line)
                    self._dispatch(msg.get("action", ""))
                except Exception:
                    pass

        self._proc.wait()
