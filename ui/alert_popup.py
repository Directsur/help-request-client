# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import threading
import tkinter as tk

import config as cfg
from core.alert import build_alert_text
from platform_support.sound import play_alert
from ui.fonts import font, mono

_popup_lock   = threading.Lock()
_active_popup = None


def show(msg: dict):
    global _active_popup
    with _popup_lock:
        if _active_popup:
            try:
                if _active_popup.winfo_exists():
                    _active_popup.destroy()
            except Exception:
                pass

    threading.Thread(target=_create_popup, args=(msg,), daemon=True).start()


def _create_popup(msg: dict):
    global _active_popup

    is_drill = bool(msg.get("is_drill", False))

    bg_main = "#e67e22" if is_drill else "#c0392b"
    bg_bar  = "#ca6f1e" if is_drill else "#a93226"
    bg_btn  = "#a04000" if is_drill else "#922b21"
    bg_btn2 = "#884000" if is_drill else "#7b241c"
    title   = "⚠  SIMULACRO — PRUEBA DEL SISTEMA" if is_drill else "⚠  SOLICITUD DE AYUDA"

    root = tk.Tk()
    root.withdraw()

    popup = tk.Toplevel(root)
    _active_popup = popup

    popup.title("SIMULACRO" if is_drill else "SOLICITUD DE AYUDA")
    popup.configure(bg=bg_main)
    popup.attributes("-topmost", True)
    popup.resizable(False, False)

    sw = popup.winfo_screenwidth()
    sh = popup.winfo_screenheight()
    w, h = 620, 320
    popup.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    tk.Label(popup, text=title, font=font(16, "bold"),
             bg=bg_main, fg="white", pady=16).pack()

    tk.Label(popup, text=build_alert_text(msg), font=font(12),
             bg=bg_main, fg="white", justify="center",
             wraplength=580, pady=8).pack()

    countdown_var = tk.StringVar(value=f"Esta ventana se cerrará en {cfg.POPUP_TIMEOUT}s")
    tk.Label(popup, textvariable=countdown_var, font=font(10),
             bg=bg_bar, fg="white", pady=6).pack(fill="x")

    tk.Button(popup, text="Entendido", font=font(12), bg=bg_btn, fg="white",
              activebackground=bg_btn2, activeforeground="white",
              relief="flat", padx=20, pady=8,
              command=popup.destroy).pack(pady=12)

    play_alert()

    remaining = [cfg.POPUP_TIMEOUT]

    def tick():
        if not popup.winfo_exists():
            return
        remaining[0] -= 1
        if remaining[0] <= 0:
            popup.destroy()
            return
        countdown_var.set(f"Esta ventana se cerrará en {remaining[0]}s")
        popup.after(1000, tick)

    popup.after(1000, tick)
    popup.protocol("WM_DELETE_WINDOW", popup.destroy)
    popup.mainloop()
