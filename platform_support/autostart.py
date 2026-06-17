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

def _enable_windows():
    import winreg
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE,
    )
    winreg.SetValueEx(key, "SolicitudAyuda", 0, winreg.REG_SZ, _executable_path())
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

_LINUX_DESKTOP = os.path.join(
    os.path.expanduser("~"), ".config", "autostart", "help-request.desktop"
)

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


def _enable_linux():
    os.makedirs(os.path.dirname(_LINUX_DESKTOP), exist_ok=True)
    with open(_LINUX_DESKTOP, "w") as f:
        f.write(_DESKTOP_CONTENT.format(exec=_executable_path()))


def _disable_linux():
    try:
        os.remove(_LINUX_DESKTOP)
    except FileNotFoundError:
        pass


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
