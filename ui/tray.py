# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import threading
from PIL import Image, ImageDraw
import pystray


def _make_icon(color: str) -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Triángulo de alerta
    draw.polygon([(32, 4), (62, 58), (2, 58)], fill=color)
    draw.polygon([(32, 18), (50, 50), (14, 50)], fill="white")
    # Signo de exclamación
    draw.rectangle([29, 26, 35, 42], fill=color)
    draw.ellipse([29, 45, 35, 51], fill=color)
    return img


_ICONS = {
    "ok":         _make_icon("#27ae60"),   # verde  — configurado y conectado
    "no_location": _make_icon("#f39c12"),  # amarillo — sin ubicación
    "no_server":  _make_icon("#e74c3c"),   # rojo — sin servidor
    "offline":    _make_icon("#7f8c8d"),   # gris  — sin ubicación y sin servidor
}


class TrayIcon:
    def __init__(self, app_cfg: dict, on_open_config, on_help, on_quit):
        self.cfg            = app_cfg
        self.on_open_config = on_open_config
        self.on_help        = on_help
        self.on_quit        = on_quit
        self._icon          = None
        self._status        = "offline"

    def _build_menu(self):
        location = self.cfg.get("room") or "Sin ubicación"
        hotkey   = self.cfg.get("hotkey_display", "Ctrl+F12")
        return pystray.Menu(
            pystray.MenuItem(f"📍 {location}", None, enabled=False),
            pystray.MenuItem(f"⌨  {hotkey} — solicitar ayuda", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Configurar ubicación...", lambda: self.on_open_config()),
            pystray.MenuItem("Ayuda...", lambda: self.on_help()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", lambda: self._quit()),
        )

    def _get_icon(self) -> Image.Image:
        return _ICONS.get(self._status, _ICONS["offline"])

    def _get_title(self) -> str:
        hotkey = self.cfg.get("hotkey_display", "Ctrl+F12")
        titles = {
            "ok":          f"Solicitudes de Ayuda | {hotkey} para pedir ayuda",
            "no_location": f"Solicitudes de Ayuda | Sin ubicación (solo recepción)",
            "no_server":   f"Solicitudes de Ayuda | {hotkey} para pedir ayuda (sin servidor)",
            "offline":     "Solicitudes de Ayuda | Sin configurar",
        }
        return titles.get(self._status, "Solicitudes de Ayuda")

    def set_status(self, has_location: bool, has_server: bool):
        if has_location and has_server:
            self._status = "ok"
        elif has_location and not has_server:
            self._status = "no_server"
        elif not has_location and has_server:
            self._status = "no_location"
        else:
            self._status = "offline"

        if self._icon:
            self._icon.icon  = self._get_icon()
            self._icon.title = self._get_title()

    def update_location(self, room: str):
        self.cfg["room"] = room
        if self._icon:
            self._icon.menu = self._build_menu()

    def _quit(self):
        if self._icon:
            self._icon.stop()
        self.on_quit()

    def run(self):
        self._icon = pystray.Icon(
            name="help-request",
            icon=self._get_icon(),
            title=self._get_title(),
            menu=self._build_menu(),
        )
        self._icon.run()
