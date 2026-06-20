# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Gestión del arranque automático con el sistema operativo."""
import os
import platform
import sys


def _executable_path() -> str:
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(sys.argv[0])


def enable():
    system = platform.system()
    if system == "Windows":
        _enable_windows()
    elif system == "Linux":
        _enable_linux()
    elif system == "Darwin":
        _enable_macos()


def disable():
    system = platform.system()
    if system == "Windows":
        _disable_windows()
    elif system == "Linux":
        _disable_linux()
    elif system == "Darwin":
        _disable_macos()


# ─── Windows ───────────────────────────────────────────────────────────────────

def _win_exec() -> str:
    """En Windows usamos la ruta fija de instalación para que el autoarranque
    sobreviva a actualizaciones y a mover el .exe original."""
    if getattr(sys, "frozen", False):
        from platform_support.updater import WIN_INSTALL
        return WIN_INSTALL
    return _executable_path()


def _enable_windows():
    import winreg
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE,
    )
    winreg.SetValueEx(key, "SolicitudAyuda", 0, winreg.REG_SZ, _win_exec())
    winreg.CloseKey(key)


def _disable_windows():
    import winreg
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.DeleteValue(key, "SolicitudAyuda")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass


# ─── Linux ─────────────────────────────────────────────────────────────────────

_LINUX_DESKTOP  = os.path.expanduser("~/.config/autostart/help-request.desktop")
_OPENBOX_AUTO   = os.path.expanduser("~/.config/openbox/autostart")
_OPENBOX_MARKER = "# SolicitudAyuda"

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


def _linux_exec() -> str:
    """En AppImages usamos la ruta de instalación fija para que autostart
    sobreviva a actualizaciones y a mover el AppImage original.
    Puede ser /usr/local/bin/ (sistema) o ~/.local/bin/ (usuario)."""
    if getattr(sys, "frozen", False):
        from platform_support.updater import get_linux_install_path
        return get_linux_install_path()
    return _executable_path()


def _enable_linux():
    exe = _linux_exec()

    # XDG autostart (.desktop) — funciona con GNOME, KDE, XFCE, lxsession…
    os.makedirs(os.path.dirname(_LINUX_DESKTOP), exist_ok=True)
    with open(_LINUX_DESKTOP, "w") as f:
        f.write(_DESKTOP_CONTENT.format(exec=exe))

    # Openbox autostart — para sesiones sin gestor de sesión XDG
    if os.path.isfile(_OPENBOX_AUTO):
        content = open(_OPENBOX_AUTO).read()
        if _OPENBOX_MARKER not in content:
            with open(_OPENBOX_AUTO, "a") as f:
                f.write(f"\n{_OPENBOX_MARKER}\n{exe} &\n")
    elif os.path.isdir(os.path.dirname(_OPENBOX_AUTO)):
        with open(_OPENBOX_AUTO, "w") as f:
            f.write(f"{_OPENBOX_MARKER}\n{exe} &\n")


def _disable_linux():
    try:
        os.remove(_LINUX_DESKTOP)
    except FileNotFoundError:
        pass

    if os.path.isfile(_OPENBOX_AUTO):
        from platform_support.updater import get_linux_install_path
        install = get_linux_install_path()
        lines = open(_OPENBOX_AUTO).readlines()
        filtered = [l for l in lines
                    if _OPENBOX_MARKER not in l and install not in l]
        with open(_OPENBOX_AUTO, "w") as f:
            f.writelines(filtered)


# ─── macOS ─────────────────────────────────────────────────────────────────────

_MACOS_PLIST = os.path.join(
    os.path.expanduser("~"), "Library", "LaunchAgents",
    "es.centrosalud.solicitudayuda.plist",
)

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


def _enable_macos():
    os.makedirs(os.path.dirname(_MACOS_PLIST), exist_ok=True)
    with open(_MACOS_PLIST, "w") as f:
        f.write(_PLIST_CONTENT.format(exec=_executable_path()))


def _disable_macos():
    try:
        os.remove(_MACOS_PLIST)
    except FileNotFoundError:
        pass
