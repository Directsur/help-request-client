# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Auto-actualización del cliente (Linux AppImage y Windows .exe).

Linux:
  1. install_to_stable_location() copia el AppImage a ~/.local/bin/SolicitudAyuda.
  2. schedule_update_check() descarga la nueva versión en segundo plano y la
     reemplaza directamente (Linux permite reemplazar ficheros en uso).
     Notifica via notify-send.

Windows:
  1. apply_pending_update() (llamar MUY al inicio de main) aplica la
     actualización descargada en el arranque anterior mediante un .bat temporal
     que copia el nuevo .exe y relanza la aplicación.
  2. install_to_stable_location() copia el .exe a
     %LOCALAPPDATA%\\SolicitudAyuda\\SolicitudAyuda.exe.
  3. schedule_update_check() descarga la nueva versión a _pending.exe y avisa
     al usuario. La actualización se aplica en el siguiente arranque.
"""
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time

import requests

GITHUB_REPO   = "Directsur/help-request-client"
ASSET_LINUX   = "SolicitudAyuda-x86_64.AppImage"
ASSET_WINDOWS = "SolicitudAyuda.exe"
STARTUP_DELAY = 60   # segundos antes de comprobar actualización

# ── rutas por plataforma ──────────────────────────────────────────────────────

LINUX_INSTALL = os.path.expanduser("~/.local/bin/SolicitudAyuda")

if platform.system() == "Windows":
    _WIN_DIR     = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "SolicitudAyuda"
    )
    WIN_INSTALL  = os.path.join(_WIN_DIR, "SolicitudAyuda.exe")
    _WIN_PENDING = os.path.join(_WIN_DIR, "SolicitudAyuda_new.exe")
    _WIN_BATCH   = os.path.join(_WIN_DIR, "apply_update.bat")
else:
    _WIN_DIR = WIN_INSTALL = _WIN_PENDING = _WIN_BATCH = ""


# ── versión embebida ──────────────────────────────────────────────────────────

def current_version() -> str:
    if getattr(sys, "frozen", False):
        try:
            with open(os.path.join(sys._MEIPASS, "version.txt")) as f:
                return f.read().strip()
        except Exception:
            pass
    return "dev"


# ── instalación en ruta fija ──────────────────────────────────────────────────

def install_to_stable_location():
    """Copia el ejecutable a su ruta fija si todavía no está ahí."""
    if not getattr(sys, "frozen", False):
        return

    system = platform.system()

    if system == "Linux":
        src = os.path.realpath(sys.executable)
        dst = os.path.realpath(LINUX_INSTALL)
        if src == dst:
            return
        try:
            os.makedirs(os.path.dirname(LINUX_INSTALL), exist_ok=True)
            shutil.copy2(src, LINUX_INSTALL)
            os.chmod(LINUX_INSTALL,
                     os.stat(LINUX_INSTALL).st_mode
                     | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except Exception:
            pass

    elif system == "Windows":
        src = os.path.realpath(sys.executable)
        dst = os.path.realpath(WIN_INSTALL)
        if src == dst:
            return
        try:
            os.makedirs(_WIN_DIR, exist_ok=True)
            shutil.copy2(src, WIN_INSTALL)
        except Exception:
            pass


# ── aplicar actualización pendiente (solo Windows) ───────────────────────────

def apply_pending_update():
    """
    Si existe SolicitudAyuda_new.exe (descargado en la sesión anterior),
    escribe un .bat que lo copia sobre el .exe principal y relanza la app,
    luego sale inmediatamente para que el .bat pueda copiar el fichero.
    Llamar al inicio de main(), antes de inicializar cualquier otra cosa.
    """
    if platform.system() != "Windows" or not getattr(sys, "frozen", False):
        return
    if not os.path.isfile(_WIN_PENDING):
        return

    batch = (
        "@echo off\n"
        "ping -n 3 127.0.0.1 > nul\n"
        f'copy /Y "{_WIN_PENDING}" "{WIN_INSTALL}"\n'
        f'del "{_WIN_PENDING}"\n'
        f'start "" "{WIN_INSTALL}"\n'
        'del "%~f0"\n'
    )
    try:
        os.makedirs(_WIN_DIR, exist_ok=True)
        with open(_WIN_BATCH, "w") as f:
            f.write(batch)
        subprocess.Popen(
            ["cmd", "/c", _WIN_BATCH],
            creationflags=0x08000000 | 0x00000008,  # CREATE_NO_WINDOW | DETACHED_PROCESS
        )
    except Exception:
        pass
    sys.exit(0)


# ── descarga de releases ──────────────────────────────────────────────────────

def _latest_release() -> dict | None:
    try:
        r = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
            timeout=10,
            headers={"Accept": "application/vnd.github.v3+json"},
        )
        return r.json() if r.ok else None
    except Exception:
        return None


def _download_to(url: str, dest: str) -> bool:
    try:
        r = requests.get(url, timeout=120, stream=True)
        if not r.ok:
            return False
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dest))
        with os.fdopen(fd, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
        if platform.system() == "Linux":
            os.chmod(tmp, os.stat(tmp).st_mode
                     | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        shutil.move(tmp, dest)
        return True
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        return False


def _notify_linux(title: str, body: str):
    try:
        subprocess.run(["notify-send", "-i", "system-software-update", title, body],
                       timeout=5, check=False)
    except Exception:
        pass


def _notify_windows(body: str):
    try:
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "[System.Windows.Forms.MessageBox]::Show("
            f"'{body}','Solicitudes de Ayuda',"
            "[System.Windows.Forms.MessageBoxButtons]::OK,"
            "[System.Windows.Forms.MessageBoxIcon]::Information)"
        )
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-Command", ps],
            creationflags=0x08000000,
        )
    except Exception:
        pass


def _update_worker():
    time.sleep(STARTUP_DELAY)

    release = _latest_release()
    if not release:
        return

    latest_tag = release.get("tag_name", "")
    if not latest_tag or latest_tag == current_version():
        return

    system = platform.system()
    asset_name = ASSET_LINUX if system == "Linux" else ASSET_WINDOWS

    asset_url = next(
        (a["browser_download_url"] for a in release.get("assets", [])
         if a["name"] == asset_name),
        None,
    )
    if not asset_url:
        return

    if system == "Linux":
        ok = _download_to(asset_url, LINUX_INSTALL)
        if ok:
            _notify_linux(
                "Solicitudes de Ayuda actualizado",
                f"Versión {latest_tag} instalada. Se aplicará al reiniciar.",
            )

    elif system == "Windows":
        os.makedirs(_WIN_DIR, exist_ok=True)
        ok = _download_to(asset_url, _WIN_PENDING)
        if ok:
            _notify_windows(
                f"Nueva versión {latest_tag} disponible.\n"
                "Se instalará automáticamente al reiniciar la aplicación."
            )


# ── punto de entrada ──────────────────────────────────────────────────────────

def schedule_update_check():
    """Lanza la comprobación de actualización en segundo plano."""
    if not getattr(sys, "frozen", False):
        return
    if platform.system() not in ("Linux", "Windows"):
        return
    threading.Thread(target=_update_worker, daemon=True, name="updater").start()
