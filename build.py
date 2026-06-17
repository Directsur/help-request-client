# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Genera el ejecutable con PyInstaller.
Uso: python build.py
"""
import os
import platform
import subprocess
import sys

NAME = "SolicitudAyuda"
SYSTEM = platform.system()

args = [
    sys.executable, "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--name", NAME,
    "--onefile",
    "--noconsole",
    "--add-data", f"ui{os.sep}*{os.pathsep}ui",
    "main.py",
]

if SYSTEM == "Windows":
    # Sin consola en Windows, arranque silencioso
    args += ["--win-private-assemblies"]

elif SYSTEM == "Darwin":
    args += [
        "--osx-bundle-identifier", "es.centrosalud.solicitudayuda",
        "--target-arch", "universal2",
    ]

print(f"Construyendo para {SYSTEM}...")
result = subprocess.run(args, check=True)

if result.returncode == 0:
    out = os.path.join("dist", NAME + (".exe" if SYSTEM == "Windows" else ""))
    print(f"\nEjectable generado: {out}")
