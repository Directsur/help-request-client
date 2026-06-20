# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import os
import platform
import socket
import uuid

_SYSTEM = platform.system()

if _SYSTEM == "Windows":
    CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "HelpRequest")
else:
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "HelpRequest")

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

UDP_PORT = 54321
API_PORT = 8080
HEARTBEAT_INTERVAL  = 30   # segundos
ALERT_DEBOUNCE      = 10   # segundos mínimos entre alertas del mismo cliente
ALERT_DEDUP_WINDOW  = 5    # segundos para descartar duplicados entrantes
POPUP_TIMEOUT       = 30   # segundos antes de cerrar el popup automáticamente

DEFAULT_HOTKEY         = "<ctrl>+<f12>"
DEFAULT_HOTKEY_DISPLAY = "Ctrl+F12"


def _get_mac() -> str:
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> (i * 8)) & 0xff:02x}' for i in reversed(range(6)))


_DEFAULTS = {
    "client_id":      _get_mac(),
    "server_ip":      None,
    "server_url":     "",   # URL manual (vacío = descubrimiento automático por UDP)
    "room_id":        None,
    "room":           "",
    "floor":          "",
    "building":       "",
    "center":         "",
    "group_id":       None,
    "is_security":    False,
    "hotkey":         DEFAULT_HOTKEY,
    "hotkey_display": DEFAULT_HOTKEY_DISPLAY,
    "peers":          [],
}


def load() -> dict:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = {**_DEFAULTS, **data}
        except Exception:
            cfg = dict(_DEFAULTS)
    else:
        cfg = dict(_DEFAULTS)
    cfg["client_id"] = _get_mac()
    return cfg


def save(cfg: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def is_location_complete(cfg: dict) -> bool:
    return bool(cfg.get("room_id") and cfg.get("room"))


def human_to_pynput(human: str) -> str:
    """Convierte 'Ctrl+F12' al formato interno de pynput '<ctrl>+<f12>'."""
    parts = human.strip().split("+")
    result = []
    for part in parts:
        p = part.strip().lower()
        if p in ("ctrl", "control"):
            result.append("<ctrl>")
        elif p == "alt":
            result.append("<alt>")
        elif p == "shift":
            result.append("<shift>")
        elif p.startswith("f") and p[1:].isdigit():
            result.append(f"<{p}>")
        elif len(p) == 1:
            result.append(p)
        else:
            result.append(f"<{p}>")
    return "+".join(result)
