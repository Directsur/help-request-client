# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Configuración automática de atajos de teclado en el entorno de ventanas
para Wayland (GNOME y KDE Plasma).

Los atajos llaman al propio ejecutable con --trigger o --drill,
que a su vez envía el comando al socket de la instancia en ejecución.
"""
import os
import shutil
import subprocess
import sys


def _executable() -> str:
    """Ruta al ejecutable actual (funciona con AppImage y con Python directo)."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(sys.argv[0])


def detect_desktop() -> str:
    """Devuelve 'gnome', 'kde' o 'unknown'."""
    de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "gnome" in de or "unity" in de or "budgie" in de:
        return "gnome"
    if "kde" in de:
        return "kde"
    return "unknown"


# ─── GNOME ────────────────────────────────────────────────────────────────────

def _gsettings(*args) -> str:
    return subprocess.check_output(["gsettings", *args], text=True).strip()


def _gsettings_set(*args):
    subprocess.run(["gsettings", "set", *args], check=True)


def _parse_gsettings_list(raw: str) -> list[str]:
    """
    Parsea la salida de gsettings para listas de strings.
    Maneja tanto '[]' como '@as []' (lista vacía tipada de GNOME 40+)
    y '['/ruta/1/', '/ruta/2/']'.
    """
    raw = raw.strip()
    # Elimina el prefijo de tipo GVariant si lo hay (@as, @aas, etc.)
    if raw.startswith("@"):
        raw = raw.split(" ", 1)[-1].strip()
    if raw in ("[]", ""):
        return []
    # Elimina corchetes exteriores
    raw = raw.strip("[]")
    # Extrae cada ruta entre comillas simples o dobles
    import re
    return re.findall(r"['\"]([^'\"]+)['\"]", raw)


def setup_gnome(hotkey_display: str):
    """
    Registra dos atajos personalizados en GNOME:
      - hotkey_display (ej. 'Ctrl+F12')  → --trigger
      - Ctrl+Shift+F12                   → --drill
    Compatible con GNOME 40-46 (Ubuntu 22.04, 24.04 y posteriores).
    """
    if not shutil.which("gsettings"):
        raise RuntimeError("gsettings no encontrado")

    base_path      = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings"
    list_key       = "org.gnome.settings-daemon.plugins.media-keys"
    binding_schema = "org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"

    try:
        raw   = _gsettings("get", list_key, "custom-keybindings")
        paths = _parse_gsettings_list(raw)
    except Exception:
        paths = []

    exec_path = _executable()
    shortcuts = [
        {
            "suffix":  "help-request-alert",
            "name":    "Solicitud de Ayuda",
            "command": f"{exec_path} --trigger",
            "binding": _human_to_gnome(hotkey_display),
        },
        {
            "suffix":  "help-request-drill",
            "name":    "Solicitud de Ayuda — Simulacro",
            "command": f"{exec_path} --drill",
            "binding": "<Control><Shift>F12",
        },
    ]

    new_paths = [p for p in paths
                 if "help-request-alert" not in p and "help-request-drill" not in p]

    for sc in shortcuts:
        path = f"{base_path}/{sc['suffix']}/"
        new_paths.append(path)
        _gsettings_set(f"{binding_schema}:{path}", "name",    sc["name"])
        _gsettings_set(f"{binding_schema}:{path}", "command", sc["command"])
        _gsettings_set(f"{binding_schema}:{path}", "binding", sc["binding"])

    paths_str = "[" + ", ".join(f"'{p}'" for p in new_paths) + "]"
    _gsettings_set(list_key, "custom-keybindings", paths_str)


def remove_gnome():
    if not shutil.which("gsettings"):
        return
    list_key = "org.gnome.settings-daemon.plugins.media-keys"
    try:
        raw      = _gsettings("get", list_key, "custom-keybindings")
        paths    = _parse_gsettings_list(raw)
        filtered = [p for p in paths
                    if "help-request-alert" not in p and "help-request-drill" not in p]
        paths_str = "[" + ", ".join(f"'{p}'" for p in filtered) + "]"
        _gsettings_set(list_key, "custom-keybindings", paths_str)
    except Exception:
        pass


def _human_to_gnome(human: str) -> str:
    """
    Convierte 'Ctrl+F12' al formato de GNOME '<Control>F12'.
    Las teclas modificadoras van entre <>, las demás (Fx, letras) van sin <>.
    Compatibe con GNOME 40-46.
    """
    modifiers = {
        "ctrl":    "<Control>",
        "control": "<Control>",
        "alt":     "<Alt>",
        "shift":   "<Shift>",
        "super":   "<Super>",
        "meta":    "<Meta>",
    }
    parts  = human.strip().split("+")
    prefix = ""
    key    = ""
    for part in parts:
        p   = part.strip()
        low = p.lower()
        if low in modifiers:
            prefix += modifiers[low]
        else:
            # Normaliza teclas de función: f12 → F12
            if low.startswith("f") and low[1:].isdigit():
                key = "F" + low[1:]
            else:
                key = p
    return prefix + key


# ─── KDE Plasma ───────────────────────────────────────────────────────────────

def _kde_tools() -> tuple[str, str]:
    """
    Devuelve (kwriteconfig, kglobalaccel) según la versión de KDE instalada.
    KDE 5 → kwriteconfig5 / kglobalaccel5
    KDE 6 → kwriteconfig6 / kglobalaccel6   (Kubuntu 24.04+)
    """
    for ver in ("6", "5"):
        if shutil.which(f"kwriteconfig{ver}"):
            return f"kwriteconfig{ver}", f"kglobalaccel{ver}"
    raise RuntimeError(
        "No se encontró kwriteconfig5 ni kwriteconfig6.\n"
        "Instala el paquete kde-cli-tools (KDE 5) o kf6-cli-tools (KDE 6)."
    )


def setup_kde(hotkey_display: str):
    """
    Registra atajos personalizados en KDE Plasma 5 y 6.
    Compatible con Kubuntu 22.04 (KDE 5) y Kubuntu 24.04 (KDE 6).
    """
    kwriteconfig, kglobalaccel = _kde_tools()

    exec_path = _executable()
    config    = os.path.join(os.path.expanduser("~"), ".config", "kglobalshortcutsrc")

    shortcuts = [
        ("SolicitudAyuda.desktop", "trigger", hotkey_display,   f"{exec_path} --trigger"),
        ("SolicitudAyuda.desktop", "drill",   "Ctrl+Shift+F12", f"{exec_path} --drill"),
    ]

    for group, key, binding, command in shortcuts:
        subprocess.run([
            kwriteconfig, "--file", config,
            "--group", group,
            "--key", key,
            f"{binding},none,{command}",
        ], check=False)

    # Recarga los atajos en KDE
    if shutil.which(kglobalaccel):
        subprocess.run([kglobalaccel, "--load"], check=False)


# ─── Entrada pública ──────────────────────────────────────────────────────────

def setup(hotkey_display: str) -> str:
    """
    Detecta el entorno y configura los atajos.
    Devuelve 'gnome', 'kde' o lanza RuntimeError si no es compatible.
    """
    de = detect_desktop()
    if de == "gnome":
        setup_gnome(hotkey_display)
        return "gnome"
    elif de == "kde":
        setup_kde(hotkey_display)
        return "kde"
    else:
        raise RuntimeError(
            f"Entorno de escritorio no reconocido: {os.environ.get('XDG_CURRENT_DESKTOP', 'desconocido')}.\n"
            "Configura manualmente un atajo que ejecute:\n"
            f"  {_executable()} --trigger"
        )
