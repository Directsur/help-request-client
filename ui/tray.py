# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import os
import platform
import threading
from PIL import Image, ImageDraw
import pystray

# En WMs ligeros sobre X11 (Openbox, i3, bspwm…) forzamos el backend XOrg
# de pystray, que usa el protocolo XEMBED compatible con tint2/polybar/etc.
# En Wayland o entornos de escritorio completos (GNOME, KDE…) dejamos que
# pystray elija su backend (AppIndicator/StatusNotifierItem).
if platform.system() == "Linux":
    _desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    _session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    _FULL_DE = {"gnome", "kde", "unity", "xfce", "lxde", "mate",
                "cinnamon", "budgie", "pantheon"}
    if _session != "wayland" and not any(d in _desktop for d in _FULL_DE):
        try:
            from pystray import _xorg as _linux_backend
            pystray.Icon = _linux_backend.Icon
        except ImportError:
            pass


def _make_icon(color: str, size: int = 64) -> Image.Image:
    # Dibujamos a 4× y reducimos con LANCZOS para obtener antialiasing
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    m = S / 64  # factor de escala respecto al diseño original a 64 px
    draw.polygon([
        (32*m,  4*m), (62*m, 58*m), (2*m, 58*m),
    ], fill=color)
    draw.polygon([
        (32*m, 18*m), (50*m, 50*m), (14*m, 50*m),
    ], fill="white")
    draw.rectangle([29*m, 26*m, 35*m, 42*m], fill=color)
    draw.ellipse([29*m, 45*m, 35*m, 51*m], fill=color)
    return img.resize((size, size), Image.LANCZOS)


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
