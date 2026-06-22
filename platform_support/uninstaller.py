# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Desinstalador limpio del cliente Solicitudes de Ayuda.

Invocado con: SolicitudAyuda --uninstall

Si se ejecuta como usuario normal elimina las entradas del usuario actual.
Si se ejecuta como root/Administrador elimina también las entradas del sistema
(/etc/xdg/autostart, HKLM, /Library/LaunchAgents, etc.).
"""
import os
import platform
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

import config


# ── privilegios ───────────────────────────────────────────────────────────────

def _is_root() -> bool:
    if platform.system() == "Windows":
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    return os.getuid() == 0


# ── diálogos ──────────────────────────────────────────────────────────────────

def _confirm(system_install: bool) -> bool:
    root = tk.Tk()
    root.withdraw()
    if system_install:
        scope = (
            "  • El ejecutable del sistema y las entradas de autoarranque globales\n"
            "  • Los datos de configuración de este usuario\n\n"
            "Nota: los datos de configuración de otros usuarios no se eliminan."
        )
    else:
        scope = (
            "  • El ejecutable de la aplicación\n"
            "  • La configuración de inicio automático de este usuario\n"
            "  • Los datos de configuración de este usuario"
        )
    ok = messagebox.askyesno(
        "Desinstalar Solicitudes de Ayuda",
        f"¿Desea desinstalar Solicitudes de Ayuda?\n\nSe eliminarán:\n{scope}\n\n"
        "Esta acción no se puede deshacer.",
        icon="warning",
    )
    root.destroy()
    return ok


def _done():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Desinstalación completada",
        "Solicitudes de Ayuda ha sido desinstalado correctamente.",
    )
    root.destroy()


def _error(msg: str):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error al desinstalar", msg)
    root.destroy()


# ── Linux ─────────────────────────────────────────────────────────────────────

def _uninstall_linux():
    from platform_support import autostart
    from platform_support.updater import LINUX_SYSTEM_INSTALL, LINUX_USER_INSTALL
    from platform_support.installer import (
        LINUX_SYSTEM_DESKTOP, LINUX_SYSTEM_OPENBOX, LINUX_OPENBOX_MARKER
    )

    root = _is_root()
    if not _confirm(system_install=root):
        return

    # Autoarranque del usuario actual
    autostart.disable()

    # Autoarranque del sistema (solo si root)
    if root:
        try:
            os.remove(LINUX_SYSTEM_DESKTOP)
        except (FileNotFoundError, PermissionError):
            pass
        if os.path.isfile(LINUX_SYSTEM_OPENBOX):
            try:
                lines = open(LINUX_SYSTEM_OPENBOX).readlines()
                filtered = [l for l in lines
                            if LINUX_OPENBOX_MARKER not in l
                            and LINUX_SYSTEM_INSTALL not in l]
                with open(LINUX_SYSTEM_OPENBOX, "w") as f:
                    f.writelines(filtered)
            except Exception:
                pass

    # Configuración del usuario actual
    shutil.rmtree(config.CONFIG_DIR, ignore_errors=True)

    # Ejecutable
    candidates = ([LINUX_SYSTEM_INSTALL] if root else []) + [LINUX_USER_INSTALL]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        try:
            os.remove(path)
            break
        except PermissionError:
            _error(
                f"No se pudo eliminar {path}.\n\n"
                f"Ejecute como root:\n  sudo {path} --uninstall"
            )
            return

    _done()


# ── Windows ───────────────────────────────────────────────────────────────────

def _uninstall_windows():
    from platform_support import autostart
    from platform_support.updater import WIN_SYSTEM_INSTALL, WIN_USER_INSTALL

    root = _is_root()
    if not _confirm(system_install=root):
        return

    # Autoarranque (elimina HKLM y HKCU)
    autostart.disable()

    # Configuración del usuario actual
    shutil.rmtree(config.CONFIG_DIR, ignore_errors=True)

    # Directorios a eliminar
    candidates = ([WIN_SYSTEM_INSTALL] if root else []) + [WIN_USER_INSTALL]
    dirs_to_remove = []
    for path in candidates:
        d = os.path.dirname(path)
        if os.path.isfile(path) and d not in dirs_to_remove:
            dirs_to_remove.append(d)

    if not dirs_to_remove:
        _done()
        return

    bat_lines = ["@echo off", "ping -n 3 127.0.0.1 > nul"]
    for d in dirs_to_remove:
        bat_lines.append(f'rmdir /S /Q "{d}"')
    bat_lines.append('del "%~f0"')

    bat_path = os.path.join(
        os.environ.get("TEMP", os.path.expanduser("~")),
        "uninstall_solicitudayuda.bat",
    )
    with open(bat_path, "w") as f:
        f.write("\n".join(bat_lines) + "\n")

    subprocess.Popen(
        ["cmd", "/c", bat_path],
        creationflags=0x08000000 | 0x00000008,  # CREATE_NO_WINDOW | DETACHED_PROCESS
    )
    _done()


# ── macOS ─────────────────────────────────────────────────────────────────────

def _uninstall_macos():
    from platform_support import autostart
    from platform_support.installer import MACOS_APP, MACOS_PLIST

    root = _is_root()
    if not _confirm(system_install=root):
        return

    # LaunchAgent del usuario actual
    autostart.disable()

    # LaunchAgent del sistema (solo si root)
    if root:
        try:
            subprocess.run(["launchctl", "unload", MACOS_PLIST], check=False)
            os.remove(MACOS_PLIST)
        except (FileNotFoundError, PermissionError):
            pass

    # Configuración del usuario actual
    shutil.rmtree(config.CONFIG_DIR, ignore_errors=True)

    # Bundle .app
    # Con root: eliminar /Applications/SolicitudAyuda.app directamente.
    # Sin root: localizar el bundle desde sys.executable.
    if root and os.path.isdir(MACOS_APP):
        bundle = MACOS_APP
    else:
        bundle = os.path.realpath(sys.executable)
        for _ in range(6):
            if bundle.endswith(".app"):
                break
            bundle = os.path.dirname(bundle)
        if not bundle.endswith(".app"):
            bundle = None

    if bundle and os.path.isdir(bundle):
        try:
            shutil.rmtree(bundle)
        except PermissionError:
            _error(
                f"No se pudo eliminar {bundle}.\n\n"
                "Ejecute como root:\n"
                f"  sudo '{sys.executable}' --uninstall\n\n"
                "O elimínelo manualmente arrastrándolo a la Papelera."
            )
            return

    _done()


# ── punto de entrada ──────────────────────────────────────────────────────────

def run():
    system = platform.system()
    if system == "Linux":
        _uninstall_linux()
    elif system == "Windows":
        _uninstall_windows()
    elif system == "Darwin":
        _uninstall_macos()

    sys.exit(0)
