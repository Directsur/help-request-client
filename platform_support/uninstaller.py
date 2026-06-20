# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Desinstalador limpio del cliente Solicitudes de Ayuda.

Invocado con: SolicitudAyuda --uninstall

Elimina:
  - El ejecutable instalado (o el bundle .app en macOS)
  - Las entradas de autoarranque (registro, .desktop, LaunchAgent, Openbox)
  - El directorio de configuración del usuario actual
"""
import os
import platform
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

import config


# ── diálogos ──────────────────────────────────────────────────────────────────

def _confirm() -> bool:
    root = tk.Tk()
    root.withdraw()
    ok = messagebox.askyesno(
        "Desinstalar Solicitudes de Ayuda",
        "¿Desea desinstalar completamente Solicitudes de Ayuda?\n\n"
        "Se eliminarán:\n"
        "  • El ejecutable de la aplicación\n"
        "  • La configuración de inicio automático\n"
        "  • Los datos de configuración de este usuario\n\n"
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

    # Autoarranque (no requiere sudo)
    autostart.disable()

    # Configuración del usuario actual
    shutil.rmtree(config.CONFIG_DIR, ignore_errors=True)

    # Ejecutable: intentar en orden sistema → usuario
    removed = False
    for path in (LINUX_SYSTEM_INSTALL, LINUX_USER_INSTALL):
        if not os.path.isfile(path):
            continue
        try:
            os.remove(path)
            removed = True
            break
        except PermissionError:
            _error(
                f"No se pudo eliminar {path} (se necesitan permisos de administrador).\n\n"
                f"Ejecute de nuevo como root:\n"
                f"  sudo {path} --uninstall"
            )
            return

    if not removed:
        # El ejecutable no está en ninguna ruta conocida (lanzado desde otra ubicación).
        # La configuración y el autoarranque ya se han eliminado.
        pass

    _done()


# ── Windows ───────────────────────────────────────────────────────────────────

def _uninstall_windows():
    from platform_support import autostart
    from platform_support.updater import WIN_SYSTEM_INSTALL, WIN_USER_INSTALL

    # Autoarranque (elimina tanto HKLM como HKCU si existen)
    autostart.disable()

    # Configuración del usuario actual
    shutil.rmtree(config.CONFIG_DIR, ignore_errors=True)

    # Determinar qué directorio de instalación eliminar
    dirs_to_remove = []
    for path in (WIN_SYSTEM_INSTALL, WIN_USER_INSTALL):
        d = os.path.dirname(path)
        if os.path.isfile(path) and d not in dirs_to_remove:
            dirs_to_remove.append(d)

    if not dirs_to_remove:
        _done()
        return

    # No se puede borrar el .exe en ejecución en Windows → .bat con retardo
    bat_lines = ["@echo off", "ping -n 3 127.0.0.1 > nul"]
    for d in dirs_to_remove:
        bat_lines.append(f'rmdir /S /Q "{d}"')
    bat_lines.append('del "%~f0"')

    bat_path = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")),
                            "uninstall_solicitudayuda.bat")
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

    # LaunchAgent (no requiere sudo)
    autostart.disable()

    # Configuración del usuario actual
    shutil.rmtree(config.CONFIG_DIR, ignore_errors=True)

    # Localizar el bundle .app subiendo desde sys.executable
    bundle = os.path.realpath(sys.executable)
    for _ in range(6):
        if bundle.endswith(".app"):
            break
        bundle = os.path.dirname(bundle)

    if bundle.endswith(".app") and os.path.isdir(bundle):
        try:
            shutil.rmtree(bundle)
        except PermissionError:
            _error(
                f"No se pudo eliminar {bundle}.\n\n"
                "Elimínelo manualmente arrastrándolo a la Papelera."
            )
            return

    _done()


# ── punto de entrada ──────────────────────────────────────────────────────────

def run():
    if not _confirm():
        return

    system = platform.system()
    if system == "Linux":
        _uninstall_linux()
    elif system == "Windows":
        _uninstall_windows()
    elif system == "Darwin":
        _uninstall_macos()

    sys.exit(0)
