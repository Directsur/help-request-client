# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import tkinter as tk
from tkinter import font as tkfont
from ui.fonts import font, mono


def show(hotkey_display: str, location_text: str, send_enabled: bool):
    root = tk.Tk()
    root.title("Solicitudes de Ayuda — Activo")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.configure(bg="#1a252f")

    w, h = 440, 380
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}+{(sw - w) // 2}+{(sh - h) // 2}")

    bold_lg = font(14, "bold")
    bold_md = font(11, "bold")
    normal  = font(10)
    mono_xl = mono(26, "bold")

    tk.Label(root, text="Solicitudes de Ayuda", font=bold_lg,
             bg="#1a252f", fg="white").pack(pady=(20, 4))

    tk.Label(root, text=f"📍 {location_text}", font=normal,
             bg="#1a252f", fg="#aed6f1").pack(pady=(0, 16))

    if send_enabled:
        tk.Label(root, text="Para solicitar ayuda, pulsa:", font=normal,
                 bg="#1a252f", fg="#ecf0f1").pack()

        key_frame = tk.Frame(root, bg="#f39c12", padx=16, pady=10)
        key_frame.pack(pady=6)
        tk.Label(key_frame, text=hotkey_display, font=mono_xl,
                 bg="#f39c12", fg="#1a252f").pack()

        tk.Label(root,
                 text="El aviso se enviará a todos los equipos de tu grupo\ny a los equipos de seguridad.",
                 font=normal, bg="#1a252f", fg="#aed6f1", justify="center").pack(pady=(2, 8))

        tk.Label(root, text="Para lanzar un simulacro (prueba del sistema):",
                 font=normal, bg="#1a252f", fg="#7f8c8d").pack()
        drill_frame = tk.Frame(root, bg="#7f8c8d", padx=10, pady=4)
        drill_frame.pack(pady=(2, 4))
        tk.Label(drill_frame, text="Ctrl+Shift+F12",
                 font=mono(13, "bold"),
                 bg="#7f8c8d", fg="white").pack()
    else:
        tk.Label(root,
                 text="⚠  Sin ubicación configurada\n\nPodrás recibir avisos de tus compañeros\npero no podrás enviar alertas.",
                 font=bold_md, bg="#1a252f", fg="#f39c12", justify="center").pack(pady=24)

    tk.Button(root, text="Entendido", font=bold_md,
              bg="#2980b9", fg="white", activebackground="#1a6ea8",
              relief="flat", padx=24, pady=6,
              command=root.destroy).pack(pady=(0, 20))

    root.mainloop()
