# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import socket
import time
import requests

import config as cfg

_SESSION = requests.Session()
_SESSION.timeout = 5


def _api(server_ip: str) -> str:
    return f"http://{server_ip}:{cfg.API_PORT}"


# ─── Descubrimiento ────────────────────────────────────────────────────────────

def discover_server(timeout: int = 3) -> str | None:
    message = json.dumps({"type": "DISCOVER"}).encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    try:
        sock.sendto(message, ("255.255.255.255", cfg.UDP_PORT))
        data, addr = sock.recvfrom(1024)
        msg = json.loads(data.decode())
        if msg.get("type") == "SERVER_HERE":
            return addr[0]
    except (socket.timeout, Exception):
        pass
    finally:
        sock.close()
    return None


# ─── Registro y heartbeat ──────────────────────────────────────────────────────

def register(server_ip: str, client_id: str, name: str) -> dict | None:
    try:
        r = _SESSION.post(
            f"{_api(server_ip)}/api/clients/{client_id}/register",
            json={"name": name},
        )
        return r.json() if r.ok else None
    except Exception:
        return None


def heartbeat(server_ip: str, client_id: str) -> list:
    try:
        r = _SESSION.post(f"{_api(server_ip)}/api/clients/{client_id}/heartbeat")
        return r.json().get("peers", []) if r.ok else []
    except Exception:
        return []


# ─── Ubicación ─────────────────────────────────────────────────────────────────

def get_location(server_ip: str, client_id: str) -> dict | None:
    try:
        r = _SESSION.get(f"{_api(server_ip)}/api/clients/{client_id}/location")
        return r.json() if r.ok else None
    except Exception:
        return None


def update_location(server_ip: str, client_id: str, room_id: int) -> bool:
    try:
        r = _SESSION.put(
            f"{_api(server_ip)}/api/clients/{client_id}/location",
            json={"room_id": room_id},
        )
        return r.ok
    except Exception:
        return False


# ─── Dropdowns para ventana de configuración ──────────────────────────────────

def get_centers(server_ip: str) -> list:
    try:
        return _SESSION.get(f"{_api(server_ip)}/api/centers").json()
    except Exception:
        return []


def get_buildings(server_ip: str, center_id: int) -> list:
    try:
        return _SESSION.get(f"{_api(server_ip)}/api/buildings", params={"center_id": center_id}).json()
    except Exception:
        return []


def get_floors(server_ip: str, building_id: int) -> list:
    try:
        return _SESSION.get(f"{_api(server_ip)}/api/floors", params={"building_id": building_id}).json()
    except Exception:
        return []


def get_rooms(server_ip: str, floor_id: int) -> list:
    try:
        return _SESSION.get(f"{_api(server_ip)}/api/rooms", params={"floor_id": floor_id}).json()
    except Exception:
        return []


def add_location_item(server_ip: str, endpoint: str, body: dict) -> dict | None:
    try:
        r = _SESSION.post(f"{_api(server_ip)}/api/{endpoint}", json=body)
        return r.json() if r.ok else None
    except Exception:
        return None


# ─── Envío de alertas ──────────────────────────────────────────────────────────

def report_alert(server_ip: str, alert: dict) -> bool:
    try:
        r = _SESSION.post(f"{_api(server_ip)}/api/alerts", json=alert)
        return r.ok
    except Exception:
        return False


def broadcast_alert(alert: dict, peers: list):
    payload = json.dumps({**alert, "type": "ALERT"}).encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        # Broadcast a toda la red
        sock.sendto(payload, ("255.255.255.255", cfg.UDP_PORT))
        # Unicast a cada peer conocido (para redes con VLANs)
        for peer in peers:
            try:
                sock.sendto(payload, (peer["ip"], cfg.UDP_PORT))
                time.sleep(0.01)
            except Exception:
                pass
    finally:
        sock.close()


def get_server_config(server_ip: str) -> dict:
    try:
        r = _SESSION.get(f"{_api(server_ip)}/api/config")
        return r.json() if r.ok else {}
    except Exception:
        return {}


def send_heartbeat_udp(client_id: str):
    payload = json.dumps({"type": "HEARTBEAT", "client_id": client_id}).encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.sendto(payload, ("255.255.255.255", cfg.UDP_PORT))
    finally:
        sock.close()
