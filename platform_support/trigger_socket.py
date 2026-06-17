# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Socket Unix local para recibir disparos externos (Wayland / scripts).

El cliente en ejecución escucha en SOCKET_PATH.
Cuando se llama al ejecutable con --trigger o --drill, conecta al socket,
envía el comando y sale inmediatamente.
"""
import os
import socket
import threading

SOCKET_PATH = os.path.join(
    os.path.expanduser("~"), ".local", "share", "HelpRequest", "trigger.sock"
)

TRIGGER_ALERT = b"ALERT\n"
TRIGGER_DRILL = b"DRILL\n"


# ─── Lado cliente (instancia nueva con --trigger / --drill) ───────────────────

def send_trigger(command: bytes) -> bool:
    """Envía un comando a la instancia en ejecución. Devuelve True si tuvo éxito."""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(SOCKET_PATH)
        sock.sendall(command)
        sock.close()
        return True
    except Exception:
        return False


# ─── Lado servidor (instancia principal) ──────────────────────────────────────

def start_listener(on_alert, on_drill):
    """
    Arranca el servidor de socket en un thread daemon.
    on_alert y on_drill son callables sin argumentos.
    """
    os.makedirs(os.path.dirname(SOCKET_PATH), exist_ok=True)

    # Elimina socket anterior si existe (el proceso anterior terminó)
    try:
        os.unlink(SOCKET_PATH)
    except FileNotFoundError:
        pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(4)
    os.chmod(SOCKET_PATH, 0o600)

    def loop():
        while True:
            try:
                conn, _ = server.accept()
                data = conn.recv(16).strip()
                conn.close()
                if data == b"ALERT":
                    threading.Thread(target=on_alert, daemon=True).start()
                elif data == b"DRILL":
                    threading.Thread(target=on_drill, daemon=True).start()
            except Exception:
                pass

    threading.Thread(target=loop, daemon=True, name="trigger-socket").start()
