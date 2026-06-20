# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Auto-actualización del cliente AppImage.

Flujo:
  1. install_to_stable_location() — copia el AppImage actual a INSTALL_PATH
     si todavía no está ahí (primera ejecución desde otra ruta).
  2. schedule_update_check()     — espera STARTUP_DELAY segundos y comprueba
     si hay una versión más nueva en GitHub Releases. Si la hay, la descarga
     y reemplaza INSTALL_PATH. El proceso en curso sigue funcionando; la nueva
     versión se usará en el próximo arranque.
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

GITHUB_REPO  = "Directsur/help-request-client"
ASSET_NAME   = "SolicitudAyuda-x86_64.AppImage"
INSTALL_PATH = os.path.expanduser("~/.local/bin/SolicitudAyuda")
STARTUP_DELAY = 60   # segundos de espera antes de comprobar actualización


# ── versión embebida ──────────────────────────────────────────────────────────

def current_version() -> str:
    """Lee la versión grabada en version.txt durante el build."""
    if getattr(sys, "frozen", False):
        try:
            path = os.path.join(sys._MEIPASS, "version.txt")
            with open(path) as f:
                return f.read().strip()
        except Exception:
            pass
    return "dev"


# ── instalación en ruta fija ──────────────────────────────────────────────────

def install_to_stable_location():
    """
    Copia el AppImage a ~/.local/bin/SolicitudAyuda si todavía no está ahí.
    Solo actúa en AppImages (sys.frozen=True) en Linux.
    """
    if platform.system() != "Linux" or not getattr(sys, "frozen", False):
        return

    current_exe = os.path.realpath(sys.executable)
    target      = os.path.realpath(INSTALL_PATH)

    if current_exe == target:
        return  # ya estamos en la ruta estable

    try:
        os.makedirs(os.path.dirname(INSTALL_PATH), exist_ok=True)
        shutil.copy2(current_exe, INSTALL_PATH)
        os.chmod(INSTALL_PATH,
                 os.stat(INSTALL_PATH).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass


# ── comprobación y descarga de actualización ──────────────────────────────────

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


def _download_asset(url: str) -> str | None:
    """Descarga el asset a un fichero temporal y devuelve su ruta."""
    try:
        r = requests.get(url, timeout=120, stream=True)
        if not r.ok:
            return None
        fd, tmp_path = tempfile.mkstemp(suffix=".AppImage")
        with os.fdopen(fd, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
        os.chmod(tmp_path,
                 os.stat(tmp_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return tmp_path
    except Exception:
        return None


def _notify(title: str, body: str):
    try:
        subprocess.run(["notify-send", "-i", "system-software-update", title, body],
                       timeout=5, check=False)
    except Exception:
        pass


def _update_worker():
    time.sleep(STARTUP_DELAY)

    release = _latest_release()
    if not release:
        return

    latest_tag = release.get("tag_name", "")
    current    = current_version()

    if latest_tag == current or not latest_tag:
        return  # ya estamos actualizados

    asset_url = next(
        (a["browser_download_url"] for a in release.get("assets", [])
         if a["name"] == ASSET_NAME),
        None,
    )
    if not asset_url:
        return

    tmp_path = _download_asset(asset_url)
    if not tmp_path:
        return

    try:
        os.makedirs(os.path.dirname(INSTALL_PATH), exist_ok=True)
        shutil.move(tmp_path, INSTALL_PATH)
        _notify(
            "Solicitudes de Ayuda actualizado",
            f"Nueva versión {latest_tag} instalada. Se aplicará al reiniciar.",
        )
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def schedule_update_check():
    """Lanza la comprobación de actualización en segundo plano."""
    if platform.system() != "Linux" or not getattr(sys, "frozen", False):
        return
    threading.Thread(target=_update_worker, daemon=True, name="updater").start()
