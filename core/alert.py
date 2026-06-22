# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import getpass
import socket
import threading
import time
from datetime import datetime

import config as cfg
from core import network

_last_sent     = 0.0
_recent_alerts: dict[str, float] = {}  # (client_id, timestamp) -> time.time()
_lock          = threading.Lock()

# Callback que la UI registra para mostrar el popup
_on_alert_callback = None


def set_alert_callback(fn):
    global _on_alert_callback
    _on_alert_callback = fn


def _do_send(app_cfg: dict, is_drill: bool):
    username = getpass.getuser()
    alert = {
        "client_id": app_cfg["client_id"],
        "hostname":  socket.gethostname(),
        "username":  username,
        "group_id":  app_cfg.get("group_id"),
        "is_drill":  is_drill,
        "location": {
            "room":     app_cfg.get("room", ""),
            "floor":    app_cfg.get("floor", ""),
            "building": app_cfg.get("building", ""),
            "center":   app_cfg.get("center", ""),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    peers = app_cfg.get("peers", [])
    network.broadcast_alert(alert, peers)

    server_ip = app_cfg.get("server_ip")
    if server_ip:
        threading.Thread(
            target=network.report_alert,
            args=(server_ip, {
                "client_id":    alert["client_id"],
                "username":     alert["username"],
                "room":         alert["location"]["room"],
                "floor":        alert["location"]["floor"],
                "building":     alert["location"]["building"],
                "center":       alert["location"]["center"],
                "group_id":     alert["group_id"],
                "is_drill":     is_drill,
                "triggered_at": alert["timestamp"],
            }),
            daemon=True,
        ).start()


def send_alert(app_cfg: dict):
    global _last_sent
    with _lock:
        now = time.time()
        if now - _last_sent < cfg.ALERT_DEBOUNCE:
            return
        _last_sent = now
    _do_send(app_cfg, is_drill=False)


def send_drill_alert(app_cfg: dict):
    global _last_sent
    with _lock:
        now = time.time()
        if now - _last_sent < cfg.ALERT_DEBOUNCE:
            return
        _last_sent = now
    _do_send(app_cfg, is_drill=True)


def on_udp_message(msg: dict, from_ip: str, app_cfg: dict):
    if msg.get("type") != "ALERT":
        return

    client_id = msg.get("client_id", "")
    timestamp = msg.get("timestamp", "")
    dedup_key = f"{client_id}|{timestamp}"

    with _lock:
        now = time.time()
        # Limpia entradas antiguas
        expired = [k for k, t in _recent_alerts.items() if now - t > cfg.ALERT_DEDUP_WINDOW]
        for k in expired:
            del _recent_alerts[k]
        if dedup_key in _recent_alerts:
            return
        _recent_alerts[dedup_key] = now

    # Filtro de grupo: security recibe todo, sin grupo recibe todo
    sender_group = msg.get("group_id")
    my_group     = app_cfg.get("group_id")
    is_security  = app_cfg.get("is_security", False)

    if not is_security and sender_group and my_group and sender_group != my_group:
        return

    if _on_alert_callback:
        _on_alert_callback(msg)


def build_alert_text(msg: dict) -> str:
    username  = msg.get("username", "desconocido")
    hostname  = msg.get("hostname") or msg.get("client_id", "desconocido")
    loc       = msg.get("location", {})
    room      = loc.get("room", "")
    floor     = loc.get("floor", "")
    building  = loc.get("building", "")
    center    = loc.get("center", "")

    parts = []
    if room:
        parts.append(f"la sala {room}")
    if floor:
        parts.append(f"la planta {floor}")
    if building:
        parts.append(f"el edificio {building}")
    if center:
        parts.append(f"el centro {center}")

    location_str = (" de ".join(parts)) if parts else "ubicación desconocida"

    if msg.get("is_drill"):
        return (
            f"El usuario {username} está simulando una solicitud de ayuda\n"
            f"desde su equipo {hostname},\n"
            f"ubicado en {location_str}.\n\n"
            f"ESTO ES UN SIMULACRO. No se requiere ninguna acción real."
        )

    return (
        f"El usuario {username} está solicitando ayuda\n"
        f"desde su equipo {hostname},\n"
        f"ubicado en {location_str}."
    )
