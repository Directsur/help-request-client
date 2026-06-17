# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import threading
from pynput import keyboard

_listeners: dict[str, keyboard.Listener] = {}


def _parse_hotkey(hotkey_str: str) -> set:
    parts = hotkey_str.lower().replace(" ", "").split("+")
    keys = set()
    for part in parts:
        if part == "<ctrl>":
            keys.add(keyboard.Key.ctrl_l)
        elif part == "<alt>":
            keys.add(keyboard.Key.alt_l)
        elif part == "<shift>":
            keys.add(keyboard.Key.shift_l)
        elif part.startswith("<") and part.endswith(">"):
            try:
                keys.add(keyboard.Key[part[1:-1]])
            except KeyError:
                pass
        elif len(part) == 1:
            keys.add(keyboard.KeyCode.from_char(part))
    return keys


def _canonical(key) -> object:
    if key in (keyboard.Key.ctrl_l,  keyboard.Key.ctrl_r):  return keyboard.Key.ctrl_l
    if key in (keyboard.Key.alt_l,   keyboard.Key.alt_r):   return keyboard.Key.alt_l
    if key in (keyboard.Key.shift_l, keyboard.Key.shift_r): return keyboard.Key.shift_l
    return key


def register(name: str, hotkey_str: str, callback):
    """Registra un hotkey con nombre. Llama de nuevo para actualizar."""
    unregister(name)

    required = set()
    for k in _parse_hotkey(hotkey_str):
        required.add(_canonical(k))

    _pressed = set()

    def on_press(key):
        _pressed.add(_canonical(key))
        if required and required.issubset(_pressed):
            threading.Thread(target=callback, daemon=True).start()

    def on_release(key):
        _pressed.discard(_canonical(key))

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()
    _listeners[name] = listener


def unregister(name: str):
    if name in _listeners:
        _listeners[name].stop()
        del _listeners[name]


def unregister_all():
    for name in list(_listeners):
        unregister(name)
