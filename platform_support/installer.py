# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Instalador del sistema (--install, requiere root/Administrador).

Copia el ejecutable a la ruta del sistema y crea el autoarranque global
para TODOS los usuarios, incluidos los que se registren en el futuro.

  Linux:   /usr/local/bin/SolicitudAyuda
           /etc/xdg/autostart/help-request.desktop   (XDG, todos los DEs)
           /etc/xdg/openbox/autostart                (Openbox, si existe)

  Windows: C:\\ProgramData\\SolicitudAyuda\\SolicitudAyuda.exe
           HKLM\\...\\CurrentVersion\\Run

  macOS:   /Applications/SolicitudAyuda.app
           /Library/LaunchAgents/es.centrosalud.solicitudayuda.plist
"""
import os
import platform
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


# ── constantes ────────────────────────────────────────────────────────────────

LINUX_EXEC           = "/usr/local/bin/SolicitudAyuda"
LINUX_SYSTEM_DESKTOP = "/etc/xdg/autostart/help-request.desktop"
LINUX_SYSTEM_OPENBOX = "/etc/xdg/openbox/autostart"
LINUX_OPENBOX_MARKER = "# SolicitudAyuda"

WIN_SYSTEM_DIR  = r"C:\ProgramData\SolicitudAyuda"
WIN_SYSTEM_EXEC = os.path.join(WIN_SYSTEM_DIR, "SolicitudAyuda.exe")
WIN_RUN_KEY     = r"Software\Microsoft\Windows\CurrentVersion\Run"

MACOS_APP   = "/Applications/SolicitudAyuda.app"
MACOS_PLIST = "/Library/LaunchAgents/es.centrosalud.solicitudayuda.plist"


# ── diálogos ──────────────────────────────────────────────────────────────────

def _confirm(details: str) -> bool:
    root = tk.Tk()
    root.withdraw()
    ok = messagebox.askyesno(
        "Instalar Solicitudes de Ayuda (sistema)",
        "Se instalará Solicitudes de Ayuda para TODOS los usuarios del equipo,\n"
        "incluidos los que se registren en el futuro.\n\n"
        f"{details}\n\n"
        "¿Desea continuar?",
    )
    root.destroy()
    return ok


def _done(msg: str):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Instalación completada", msg)
    root.destroy()


def _error(msg: str):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error de instalación", msg)
    root.destroy()


def _need_root():
    root = tk.Tk()
    root.withdraw()
    system = platform.system()
    if system == "Windows":
        hint = "Ejecute el instalador con 'Ejecutar como administrador'."
    else:
        hint = f"Ejecute: sudo {os.path.realpath(sys.executable)} --install"
    messagebox.showerror(
        "Permisos insuficientes",
        "La instalación del sistema requiere permisos de administrador.\n\n" + hint,
    )
    root.destroy()


# ── comprobación de privilegios ───────────────────────────────────────────────

def _is_root() -> bool:
    if platform.system() == "Windows":
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    return os.getuid() == 0


# ── Linux ─────────────────────────────────────────────────────────────────────

_DESKTOP_CONTENT = """\
[Desktop Entry]
Type=Application
Name=Solicitudes de Ayuda
Comment=Cliente del sistema de solicitudes de ayuda
Exec={exec}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""


def _install_linux():
    src = os.path.realpath(sys.executable)

    details = (
        f"Ejecutable:    {LINUX_EXEC}\n"
        f"Autoarranque:  {LINUX_SYSTEM_DESKTOP}"
    )
    if not _confirm(details):
        return

    # 1. Copiar/actualizar ejecutable
    try:
        os.makedirs(os.path.dirname(LINUX_EXEC), exist_ok=True)
        if src != os.path.realpath(LINUX_EXEC):
            shutil.copy2(src, LINUX_EXEC)
        import stat as _stat
        os.chmod(LINUX_EXEC, os.stat(LINUX_EXEC).st_mode
                 | _stat.S_IXUSR | _stat.S_IXGRP | _stat.S_IXOTH)
    except Exception as e:
        _error(f"No se pudo instalar el ejecutable:\n{e}")
        return

    # 2. Autoarranque XDG del sistema (todos los DEs, todos los usuarios)
    try:
        os.makedirs(os.path.dirname(LINUX_SYSTEM_DESKTOP), exist_ok=True)
        with open(LINUX_SYSTEM_DESKTOP, "w") as f:
            f.write(_DESKTOP_CONTENT.format(exec=LINUX_EXEC))
    except Exception as e:
        _error(f"No se pudo crear el autoarranque XDG:\n{e}")
        return

    # 3. Openbox del sistema (opcional)
    openbox_dir = os.path.dirname(LINUX_SYSTEM_OPENBOX)
    if os.path.isdir(openbox_dir):
        try:
            if os.path.isfile(LINUX_SYSTEM_OPENBOX):
                content = open(LINUX_SYSTEM_OPENBOX).read()
                if LINUX_OPENBOX_MARKER not in content:
                    with open(LINUX_SYSTEM_OPENBOX, "a") as f:
                        f.write(f"\n{LINUX_OPENBOX_MARKER}\n{LINUX_EXEC} &\n")
            else:
                with open(LINUX_SYSTEM_OPENBOX, "w") as f:
                    f.write(f"{LINUX_OPENBOX_MARKER}\n{LINUX_EXEC} &\n")
        except Exception:
            pass  # Openbox es opcional; no abortar si falla

    _done(
        f"Solicitudes de Ayuda instalado en {LINUX_EXEC}\n\n"
        "La aplicación arrancará automáticamente para todos los usuarios\n"
        "al iniciar sesión (incluidos los que se creen en el futuro).\n\n"
        "Cada usuario configurará su propia ubicación la primera vez\n"
        "que inicie sesión."
    )


# ── Windows ───────────────────────────────────────────────────────────────────

def _install_windows():
    src = os.path.realpath(sys.executable)

    details = (
        f"Ejecutable:    {WIN_SYSTEM_EXEC}\n"
        f"Autoarranque:  HKLM\\...\\CurrentVersion\\Run  (todos los usuarios)"
    )
    if not _confirm(details):
        return

    # 1. Copiar/actualizar ejecutable
    try:
        os.makedirs(WIN_SYSTEM_DIR, exist_ok=True)
        if src != os.path.realpath(WIN_SYSTEM_EXEC):
            shutil.copy2(src, WIN_SYSTEM_EXEC)
    except Exception as e:
        _error(f"No se pudo instalar el ejecutable:\n{e}")
        return

    # 2. Autoarranque HKLM (todos los usuarios, incluidos los futuros)
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, WIN_RUN_KEY, 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "SolicitudAyuda", 0, winreg.REG_SZ, WIN_SYSTEM_EXEC)
        winreg.CloseKey(key)
    except Exception as e:
        _error(f"No se pudo registrar el autoarranque:\n{e}")
        return

    _done(
        f"Solicitudes de Ayuda instalado en:\n{WIN_SYSTEM_EXEC}\n\n"
        "La aplicación arrancará automáticamente para todos los usuarios\n"
        "al iniciar sesión (incluidos los que se creen en el futuro).\n\n"
        "Cada usuario configurará su propia ubicación la primera vez\n"
        "que inicie sesión."
    )


# ── macOS ─────────────────────────────────────────────────────────────────────

_PLIST_CONTENT = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>es.centrosalud.solicitudayuda</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exec}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""


def _find_bundle() -> str | None:
    """Sube desde sys.executable hasta encontrar el .app."""
    path = os.path.realpath(sys.executable)
    for _ in range(6):
        if path.endswith(".app"):
            return path
        path = os.path.dirname(path)
    return None


def _install_macos():
    bundle = _find_bundle()
    if not bundle:
        _error(
            "No se pudo localizar el bundle .app.\n"
            "Ejecute el instalador desde el .dmg descargado."
        )
        return

    exec_path = os.path.join(MACOS_APP, "Contents", "MacOS", "SolicitudAyuda")

    details = (
        f"Aplicación:    {MACOS_APP}\n"
        f"Autoarranque:  {MACOS_PLIST}"
    )
    if not _confirm(details):
        return

    # 1. Copiar/reemplazar .app en /Applications/
    try:
        if os.path.isdir(MACOS_APP):
            shutil.rmtree(MACOS_APP)
        shutil.copytree(bundle, MACOS_APP)
    except Exception as e:
        _error(f"No se pudo instalar la aplicación:\n{e}")
        return

    # 2. LaunchAgent del sistema (/Library/LaunchAgents/ → todos los usuarios)
    try:
        os.makedirs(os.path.dirname(MACOS_PLIST), exist_ok=True)
        with open(MACOS_PLIST, "w") as f:
            f.write(_PLIST_CONTENT.format(exec=exec_path))
        subprocess.run(["launchctl", "load", MACOS_PLIST], check=False)
    except Exception as e:
        _error(f"No se pudo crear el LaunchAgent del sistema:\n{e}")
        return

    _done(
        f"Solicitudes de Ayuda instalado en {MACOS_APP}\n\n"
        "La aplicación arrancará automáticamente para todos los usuarios\n"
        "al iniciar sesión (incluidos los que se creen en el futuro).\n\n"
        "Cada usuario configurará su propia ubicación la primera vez\n"
        "que inicie sesión."
    )


# ── punto de entrada ──────────────────────────────────────────────────────────

def run():
    if not _is_root():
        _need_root()
        sys.exit(1)

    system = platform.system()
    if system == "Linux":
        _install_linux()
    elif system == "Windows":
        _install_windows()
    elif system == "Darwin":
        _install_macos()

    sys.exit(0)
