# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Comprobación y solicitud del permiso de Accesibilidad en macOS.
Sin este permiso, pynput no puede capturar hotkeys globales.
"""
import ctypes
import ctypes.util
import subprocess
import sys


def is_accessibility_granted() -> bool:
    """Comprueba si el proceso tiene permiso de Accesibilidad."""
    if sys.platform != "darwin":
        return True
    try:
        lib = ctypes.cdll.LoadLibrary(
            "/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices"
        )
        return bool(lib.AXIsProcessTrusted())
    except Exception:
        return False


def request_accessibility():
    """
    Abre el panel de Accesibilidad en Preferencias del Sistema
    y muestra instrucciones al usuario.
    Funciona en macOS 12 Monterey y posteriores (incluido 13, 14, 15).
    """
    # En macOS 13+ se usa System Settings; en versiones anteriores System Preferences
    # El URL universal funciona en ambos
    subprocess.run([
        "open",
        "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
    ], check=False)


def show_accessibility_dialog():
    """Muestra un diálogo explicativo y abre las preferencias."""
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(
        "Permiso de Accesibilidad requerido",
        "Para que los atajos de teclado funcionen, esta aplicación\n"
        "necesita permiso de Accesibilidad.\n\n"
        "Se abrirá la pantalla de Privacidad y Seguridad.\n\n"
        "1. Haz clic en el candado para desbloquear\n"
        "2. Activa 'SolicitudAyuda' en la lista\n"
        "3. Reinicia la aplicación\n\n"
        "Sin este permiso, recibirás los avisos de tus compañeros\n"
        "pero no podrás enviar alertas con el atajo de teclado.",
    )
    root.destroy()
    request_accessibility()


def ensure_accessibility() -> bool:
    """
    Comprueba el permiso. Si no está concedido, muestra el diálogo
    y devuelve False para que la aplicación arranque en modo solo-recepción.
    """
    if is_accessibility_granted():
        return True
    show_accessibility_dialog()
    return False
