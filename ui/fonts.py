# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import platform

_SYSTEM = platform.system()

if _SYSTEM == "Windows":
    SANS  = "Segoe UI"
    MONO  = "Consolas"
elif _SYSTEM == "Darwin":
    SANS  = "SF Pro Text"
    MONO  = "SF Mono"
else:
    SANS  = "DejaVu Sans"
    MONO  = "DejaVu Sans Mono"


def font(size: int, weight: str = "normal") -> tuple:
    return (SANS, size, weight)


def mono(size: int, weight: str = "normal") -> tuple:
    return (MONO, size, weight)
