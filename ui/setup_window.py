# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import tkinter as tk
from tkinter import messagebox, ttk

from core import network
import config as cfg
from ui.fonts import font, mono, SANS


class SetupWindow:
    def __init__(self, app_cfg: dict, on_confirm, on_skip):
        self.cfg        = app_cfg
        self.on_confirm = on_confirm
        self.on_skip    = on_skip
        # Usa la URL manual si está configurada; si no, el IP descubierto por UDP
        self.server_ip  = app_cfg.get("server_url") or app_cfg.get("server_ip")

        self.root = tk.Tk()
        self.root.title("Configuración de ubicación — Solicitudes de Ayuda")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Datos cargados desde el servidor
        self._centers:   list[dict] = []
        self._buildings: list[dict] = []
        self._floors:    list[dict] = []
        self._rooms:     list[dict] = []

        self._build_ui()
        self._load_centers()

        w, h = 520, 450
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ──────────────────────────────────────────────────────────────────────────
    # Construcción de la UI
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Cabecera
        tk.Label(self.root,
                 text="Solicitudes de Ayuda",
                 font=font(14, "bold")).pack(pady=(16, 2))
        tk.Label(self.root,
                 text="Confirma o corrige la ubicación de este equipo:",
                 font=font(10)).pack(pady=(0, 10))

        # ── URL manual del servidor ──
        url_frame = tk.Frame(self.root, bg="#1a252f", pady=5)
        url_frame.pack(fill="x", padx=24, pady=(0, 8))
        url_frame.columnconfigure(1, weight=1)
        tk.Label(url_frame, text="Servidor:", anchor="w", width=10,
                 bg="#1a252f", fg="#aed6f1", font=font(9)).grid(
            row=0, column=0, padx=(8, 6), sticky="w")
        # Si el servidor se detectó por UDP sin URL manual, mostrar la URL completa
        _discovered_ip = self.cfg.get("server_ip") if not self.cfg.get("server_url") else None
        initial_url = self.cfg.get("server_url", "") or (
            f"http://{_discovered_ip}:{cfg.API_PORT}" if _discovered_ip else ""
        )
        self.server_url_var = tk.StringVar(value=initial_url)
        self.server_url_entry = tk.Entry(url_frame, textvariable=self.server_url_var,
                                          width=28, font=font(9), bg="#253444", fg="white",
                                          insertbackground="white",
                                          relief="flat")
        self.server_url_entry.grid(row=0, column=1, padx=(0, 6), sticky="ew", ipady=3)
        tk.Button(url_frame, text="Conectar", font=font(9),
                  relief="flat", bg="#2980b9", fg="white",
                  activebackground="#1a6ea8", cursor="hand2",
                  command=self._connect_manual_url).grid(row=0, column=2, padx=(0, 8))
        if self.server_ip:
            auto_status = ("Detectado automáticamente" if _discovered_ip else "")
            status_color = "#27ae60"
        else:
            auto_status = "Sin servidor detectado — introduce la URL y pulsa Conectar"
            status_color = "#e74c3c"
        self._url_status = tk.Label(url_frame, text=auto_status,
                                     bg="#1a252f", fg=status_color, font=font(8))
        self._url_status.grid(row=1, column=0, columnspan=3, padx=8, sticky="w")

        # Grid de selects
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=24)
        frame.columnconfigure(1, weight=1)

        LABEL_W = 10
        CB_W    = 34

        # ── Centro ──
        tk.Label(frame, text="Centro:", anchor="w", width=LABEL_W,
                 font=font(10)).grid(row=0, column=0, padx=(0, 6), pady=5, sticky="w")
        self.center_var = tk.StringVar()
        self.center_cb  = ttk.Combobox(frame, textvariable=self.center_var,
                                        state="readonly", width=CB_W, font=(SANS, 10))
        self.center_cb.grid(row=0, column=1, pady=5, sticky="ew")
        self.center_add = tk.Button(frame, text=" + ", font=font(9),
                                     relief="flat", bg="#2980b9", fg="white",
                                     activebackground="#1a6ea8", cursor="hand2",
                                     command=lambda: self._add_item("center"))
        self.center_add.grid(row=0, column=2, padx=(6, 0), pady=5)
        self.center_cb.bind("<<ComboboxSelected>>", lambda _: self._on_center_change())

        # ── Edificio ──
        tk.Label(frame, text="Edificio:", anchor="w", width=LABEL_W,
                 font=font(10)).grid(row=1, column=0, padx=(0, 6), pady=5, sticky="w")
        self.building_var = tk.StringVar()
        self.building_cb  = ttk.Combobox(frame, textvariable=self.building_var,
                                           state="disabled", width=CB_W, font=(SANS, 10))
        self.building_cb.grid(row=1, column=1, pady=5, sticky="ew")
        self.building_add = tk.Button(frame, text=" + ", font=font(9),
                                       relief="flat", bg="#2980b9", fg="white",
                                       activebackground="#1a6ea8", cursor="hand2",
                                       state="disabled",
                                       command=lambda: self._add_item("building"))
        self.building_add.grid(row=1, column=2, padx=(6, 0), pady=5)
        self.building_cb.bind("<<ComboboxSelected>>", lambda _: self._on_building_change())

        # ── Planta ──
        tk.Label(frame, text="Planta:", anchor="w", width=LABEL_W,
                 font=font(10)).grid(row=2, column=0, padx=(0, 6), pady=5, sticky="w")
        self.floor_var = tk.StringVar()
        self.floor_cb  = ttk.Combobox(frame, textvariable=self.floor_var,
                                       state="disabled", width=CB_W, font=(SANS, 10))
        self.floor_cb.grid(row=2, column=1, pady=5, sticky="ew")
        self.floor_add = tk.Button(frame, text=" + ", font=font(9),
                                    relief="flat", bg="#2980b9", fg="white",
                                    activebackground="#1a6ea8", cursor="hand2",
                                    state="disabled",
                                    command=lambda: self._add_item("floor"))
        self.floor_add.grid(row=2, column=2, padx=(6, 0), pady=5)
        self.floor_cb.bind("<<ComboboxSelected>>", lambda _: self._on_floor_change())

        # ── Sala ──
        tk.Label(frame, text="Sala:", anchor="w", width=LABEL_W,
                 font=font(10)).grid(row=3, column=0, padx=(0, 6), pady=5, sticky="w")
        self.room_var = tk.StringVar()
        self.room_cb  = ttk.Combobox(frame, textvariable=self.room_var,
                                      state="disabled", width=CB_W, font=(SANS, 10))
        self.room_cb.grid(row=3, column=1, pady=5, sticky="ew")
        self.room_add = tk.Button(frame, text=" + ", font=font(9),
                                   relief="flat", bg="#2980b9", fg="white",
                                   activebackground="#1a6ea8", cursor="hand2",
                                   state="disabled",
                                   command=lambda: self._add_item("room"))
        self.room_add.grid(row=3, column=2, padx=(6, 0), pady=5)

        # ── Equipo de seguridad ──
        self.security_var = tk.BooleanVar(value=self.cfg.get("is_security", False))
        tk.Checkbutton(self.root,
                       text="Este equipo es de seguridad/guardia (recibe todos los avisos)",
                       variable=self.security_var,
                       font=font(9)).pack(anchor="w", padx=24, pady=(8, 0))

        # ── Atajo activo ──
        hotkey_display = self.cfg.get("hotkey_display", cfg.DEFAULT_HOTKEY_DISPLAY)
        hk_frame = tk.Frame(self.root, bg="#1a252f", pady=6)
        hk_frame.pack(fill="x", padx=24, pady=(8, 0))
        tk.Label(hk_frame, text="Combinación para solicitar ayuda:",
                 font=font(9), bg="#1a252f", fg="#aed6f1").pack(side="left", padx=(8, 6))
        tk.Label(hk_frame, text=hotkey_display,
                 font=mono(12, "bold"), bg="#f39c12", fg="#1a252f",
                 padx=8, pady=2).pack(side="left")


        # ── Botón confirmar ──
        self.confirm_btn = tk.Button(
            self.root, text="Confirmar ubicación",
            font=font(11, "bold"),
            bg="#27ae60", fg="white",
            activebackground="#1e8449",
            relief="flat", padx=20, pady=8,
            cursor="hand2",
            command=self._confirm,
        )
        self.confirm_btn.pack(pady=14)

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers de estado de controles
    # ──────────────────────────────────────────────────────────────────────────

    def _set_cb_state(self, cb: ttk.Combobox, btn: tk.Button, enabled: bool):
        """Habilita o deshabilita un combobox y su botón [+] en bloque."""
        cb.config(state="readonly" if enabled else "disabled")
        btn.config(state="normal" if enabled else "disabled")

    def _connect_manual_url(self):
        url = self.server_url_var.get().strip()
        if url and not (url.startswith("http://") or url.startswith("https://")):
            url = "http://" + url
            self.server_url_var.set(url)
        self.server_ip = url or None
        self._centers = []
        self._url_status.config(
            text="Conectando..." if url else "Descubrimiento automático por red local",
            fg="#f39c12"
        )
        self.root.update_idletasks()
        if url:
            if network.ping(self.server_ip):
                self._url_status.config(text="Conectado", fg="#27ae60")
                self._load_centers()
            else:
                self.server_ip = None
                self._url_status.config(text="No se pudo conectar. Comprueba la URL.", fg="#e74c3c")
        else:
            self._load_centers()
            self._url_status.config(text="Usando descubrimiento automático", fg="#7fb3d3")

    def _reset_downstream(self, from_level: str):
        """Limpia y deshabilita todos los niveles por debajo del indicado."""
        levels = ["building", "floor", "room"]
        start  = levels.index(from_level)
        widgets = [
            (self.building_var, self.building_cb, self.building_add, self._buildings),
            (self.floor_var,    self.floor_cb,    self.floor_add,    self._floors),
            (self.room_var,     self.room_cb,     self.room_add,     self._rooms),
        ]
        for i in range(start, len(levels)):
            var, cb, btn, _ = widgets[i]
            var.set("")
            cb["values"] = []
            self._set_cb_state(cb, btn, False)
        # También limpia las listas internas
        if start <= 0: self._buildings = []
        if start <= 1: self._floors = []
        if start <= 2: self._rooms = []

    # ──────────────────────────────────────────────────────────────────────────
    # Carga en cascada
    # ──────────────────────────────────────────────────────────────────────────

    def _load_centers(self):
        if self.server_ip:
            self._centers = network.get_centers(self.server_ip)

        names = [c["name"] for c in self._centers]
        self.center_cb["values"] = names

        # Preseleccionar el valor guardado
        saved = self.cfg.get("center", "")
        if saved and saved in names:
            self.center_var.set(saved)
            self._on_center_change(_preselect_building=self.cfg.get("building", ""))
        else:
            self.center_var.set("")
            self._reset_downstream("building")

    def _on_center_change(self, _preselect_building: str = ""):
        center_name = self.center_var.get()
        center = next((c for c in self._centers if c["name"] == center_name), None)

        self._reset_downstream("building")

        if not center:
            return

        if self.server_ip:
            self._buildings = network.get_buildings(self.server_ip, center["id"])

        names = [b["name"] for b in self._buildings]
        self.building_cb["values"] = names
        self._set_cb_state(self.building_cb, self.building_add,
                           enabled=bool(self.server_ip))

        if _preselect_building and _preselect_building in names:
            self.building_var.set(_preselect_building)
            self._on_building_change(_preselect_floor=self.cfg.get("floor", ""))

    def _on_building_change(self, _preselect_floor: str = ""):
        building_name = self.building_var.get()
        building = next((b for b in self._buildings if b["name"] == building_name), None)

        self._reset_downstream("floor")

        if not building:
            return

        if self.server_ip:
            self._floors = network.get_floors(self.server_ip, building["id"])

        names = [f["name"] for f in self._floors]
        self.floor_cb["values"] = names
        self._set_cb_state(self.floor_cb, self.floor_add,
                           enabled=bool(self.server_ip))

        if _preselect_floor and _preselect_floor in names:
            self.floor_var.set(_preselect_floor)
            self._on_floor_change(_preselect_room=self.cfg.get("room", ""))

    def _on_floor_change(self, _preselect_room: str = ""):
        floor_name = self.floor_var.get()
        floor = next((f for f in self._floors if f["name"] == floor_name), None)

        self._reset_downstream("room")

        if not floor:
            return

        if self.server_ip:
            self._rooms = network.get_rooms(self.server_ip, floor["id"])

        names = [r["name"] for r in self._rooms]
        self.room_cb["values"] = names
        self._set_cb_state(self.room_cb, self.room_add,
                           enabled=bool(self.server_ip))

        if _preselect_room and _preselect_room in names:
            self.room_var.set(_preselect_room)

    # ──────────────────────────────────────────────────────────────────────────
    # Diálogo [+] para añadir nuevo elemento
    # ──────────────────────────────────────────────────────────────────────────

    def _add_item(self, kind: str):
        if not self.server_ip:
            messagebox.showwarning(
                "Sin conexión al servidor",
                "Para añadir nuevos elementos necesitas conexión con el servidor.\n"
                "Comprueba que el servidor está en marcha y vuelve a intentarlo.",
                parent=self.root,
            )
            return

        labels = {
            "center":   "centro",
            "building": "edificio",
            "floor":    "planta",
            "room":     "sala",
        }
        label = labels[kind]

        # Validar que el padre está seleccionado
        if kind == "building" and not self.center_var.get():
            messagebox.showerror("Selecciona primero un centro",
                                 "Debes seleccionar un centro antes de añadir un edificio.",
                                 parent=self.root)
            return
        if kind == "floor" and not self.building_var.get():
            messagebox.showerror("Selecciona primero un edificio",
                                 "Debes seleccionar un edificio antes de añadir una planta.",
                                 parent=self.root)
            return
        if kind == "room" and not self.floor_var.get():
            messagebox.showerror("Selecciona primero una planta",
                                 "Debes seleccionar una planta antes de añadir una sala.",
                                 parent=self.root)
            return

        # Construir diálogo
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Añadir {label}")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self.root)

        tk.Label(dialog, text=f"Nombre del {label}:", font=font(10)).pack(padx=20, pady=(14, 4))
        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, width=32, font=font(10))
        name_entry.pack(padx=20)
        name_entry.focus_set()

        address_var = tk.StringVar()
        if kind in ("center", "building"):
            tk.Label(dialog, text="Dirección completa (opcional):",
                     font=font(9)).pack(padx=20, pady=(10, 4))
            tk.Entry(dialog, textvariable=address_var, width=32, font=font(10)).pack(padx=20)

        status_lbl = tk.Label(dialog, text="", fg="red", font=font(9))
        status_lbl.pack(pady=(4, 0))

        def save():
            name = name_var.get().strip()
            if not name:
                status_lbl.config(text=f"El nombre del {label} no puede estar vacío.")
                return

            body: dict = {"name": name}
            if address_var.get().strip():
                body["address"] = address_var.get().strip()

            if kind == "center":
                result = network.add_location_item(self.server_ip, "centers", body)
                if result:
                    self._centers.append(result)
                    self.center_cb["values"] = [c["name"] for c in self._centers]
                    self.center_var.set(result["name"])
                    self._on_center_change()

            elif kind == "building":
                center = next((c for c in self._centers if c["name"] == self.center_var.get()), None)
                body["center_id"] = center["id"]
                result = network.add_location_item(self.server_ip, "buildings", body)
                if result:
                    self._buildings.append(result)
                    self.building_cb["values"] = [b["name"] for b in self._buildings]
                    self._set_cb_state(self.building_cb, self.building_add, True)
                    self.building_var.set(result["name"])
                    self._on_building_change()

            elif kind == "floor":
                building = next((b for b in self._buildings if b["name"] == self.building_var.get()), None)
                body["building_id"] = building["id"]
                result = network.add_location_item(self.server_ip, "floors", body)
                if result:
                    self._floors.append(result)
                    self.floor_cb["values"] = [f["name"] for f in self._floors]
                    self._set_cb_state(self.floor_cb, self.floor_add, True)
                    self.floor_var.set(result["name"])
                    self._on_floor_change()

            elif kind == "room":
                floor = next((f for f in self._floors if f["name"] == self.floor_var.get()), None)
                body["floor_id"] = floor["id"]
                result = network.add_location_item(self.server_ip, "rooms", body)
                if result:
                    self._rooms.append(result)
                    self.room_cb["values"] = [r["name"] for r in self._rooms]
                    self._set_cb_state(self.room_cb, self.room_add, True)
                    self.room_var.set(result["name"])

            if result:
                dialog.destroy()
            else:
                status_lbl.config(
                    text=f"No se pudo añadir el {label}. Comprueba la conexión con el servidor."
                )

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=14)
        tk.Button(btn_frame, text="Guardar", font=font(10, "bold"),
                  bg="#27ae60", fg="white", activebackground="#1e8449",
                  relief="flat", padx=14, pady=4, cursor="hand2",
                  command=save).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancelar", font=font(10),
                  relief="flat", padx=14, pady=4, cursor="hand2",
                  command=dialog.destroy).pack(side="left", padx=6)

        dialog.bind("<Return>", lambda _: save())
        dialog.bind("<Escape>", lambda _: dialog.destroy())
        dialog.wait_window()

    # ──────────────────────────────────────────────────────────────────────────
    # Confirmar / cerrar
    # ──────────────────────────────────────────────────────────────────────────

    def _confirm(self):
        center_name   = self.center_var.get().strip()
        building_name = self.building_var.get().strip()
        floor_name    = self.floor_var.get().strip()
        room_name     = self.room_var.get().strip()

        missing = []
        if not center_name:   missing.append("Centro")
        if not building_name: missing.append("Edificio")
        if not floor_name:    missing.append("Planta")
        if not room_name:     missing.append("Sala")

        if missing:
            messagebox.showerror(
                "Ubicación incompleta",
                "Los siguientes campos son obligatorios:\n\n  • " + "\n  • ".join(missing),
                parent=self.root,
            )
            return

        room = next((r for r in self._rooms if r["name"] == room_name), None)

        updates = {
            "room_id":     room["id"] if room else None,
            "room":        room_name,
            "floor":       floor_name,
            "building":    building_name,
            "center":      center_name,
            "is_security": self.security_var.get(),
            "server_url":  self.server_url_var.get().strip(),
        }

        if self.server_ip and room:
            network.update_location(self.server_ip, self.cfg["client_id"], room["id"])

        self.root.destroy()
        self.on_confirm(updates)

    def _on_close(self):
        if not cfg.is_location_complete(self.cfg):
            answer = messagebox.askyesno(
                "Ubicación no configurada",
                "Si cierras sin introducir la ubicación,\n"
                "podrás recibir los avisos de tus compañeros\n"
                "pero no podrás enviar alertas.\n\n"
                "¿Deseas continuar sin configurar la ubicación?",
                parent=self.root,
            )
            if not answer:
                return
        self.root.destroy()
        self.on_skip()

    def run(self):
        self.root.mainloop()
