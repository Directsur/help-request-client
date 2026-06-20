#!/usr/bin/env python3
# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Helper de bandeja GTK. Se ejecuta con el Python del sistema (fuera del bundle
PyInstaller) para usar Gtk.StatusIcon, que es compatible con tint2/XEmbed.
Protocolo: JSON por stdin (comandos) / stdout (acciones), una línea por mensaje.
"""
import base64
import json
import signal
import sys
import threading

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, GLib, GdkPixbuf
except Exception as e:
    sys.stderr.write(f"GTK no disponible: {e}\n")
    sys.exit(1)


class TrayHelper:
    def __init__(self):
        self._icon = Gtk.StatusIcon()
        self._icon.set_visible(True)
        self._icon.connect("activate", self._on_activate)
        self._icon.connect("popup-menu", self._on_popup_menu)
        self._room   = "Sin ubicación"
        self._hotkey = "Ctrl+F12"

    # ── comunicación ────────────────────────────────────────────────────────
    def _send(self, data: dict):
        sys.stdout.write(json.dumps(data) + "\n")
        sys.stdout.flush()

    # ── eventos ─────────────────────────────────────────────────────────────
    def _on_activate(self, icon):
        self._send({"action": "open_config"})

    def _on_popup_menu(self, icon, button, time):
        menu = Gtk.Menu()

        for label in (f"📍 {self._room}",
                      f"⌨  {self._hotkey} — solicitar ayuda"):
            item = Gtk.MenuItem(label=label)
            item.set_sensitive(False)
            menu.append(item)

        menu.append(Gtk.SeparatorMenuItem())

        cfg_item = Gtk.MenuItem(label="Configurar ubicación...")
        cfg_item.connect("activate", lambda w: self._send({"action": "open_config"}))
        menu.append(cfg_item)

        help_item = Gtk.MenuItem(label="Ayuda...")
        help_item.connect("activate", lambda w: self._send({"action": "help"}))
        menu.append(help_item)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Salir")
        quit_item.connect("activate", lambda w: self._send({"action": "quit"}))
        menu.append(quit_item)

        menu.show_all()
        menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

    # ── comandos entrantes ───────────────────────────────────────────────────
    def handle_command(self, cmd: dict):
        t = cmd.get("cmd")
        if t == "set_icon":
            try:
                data   = base64.b64decode(cmd["png_b64"])
                loader = GdkPixbuf.PixbufLoader.new_with_type("png")
                loader.write(data)
                loader.close()
                pixbuf = loader.get_pixbuf()
                GLib.idle_add(self._icon.set_from_pixbuf, pixbuf)
            except Exception as e:
                sys.stderr.write(f"error icono: {e}\n")
        elif t == "set_tooltip":
            GLib.idle_add(self._icon.set_tooltip_text, cmd.get("text", ""))
        elif t == "set_menu":
            self._room   = cmd.get("room",   "Sin ubicación")
            self._hotkey = cmd.get("hotkey", "Ctrl+F12")
        elif t == "quit":
            GLib.idle_add(Gtk.main_quit)

    def _stdin_reader(self):
        for line in sys.stdin:
            line = line.strip()
            if line:
                try:
                    self.handle_command(json.loads(line))
                except Exception as e:
                    sys.stderr.write(f"error comando: {e}\n")
        GLib.idle_add(Gtk.main_quit)

    def run(self):
        t = threading.Thread(target=self._stdin_reader, daemon=True)
        t.start()
        signal.signal(signal.SIGINT, lambda s, f: Gtk.main_quit())
        Gtk.main()


if __name__ == "__main__":
    TrayHelper().run()
