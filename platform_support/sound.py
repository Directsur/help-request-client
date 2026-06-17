# Copyright (C) 2025-2026 Direct Sevilla Global Services SL
# SPDX-License-Identifier: AGPL-3.0-or-later
import platform
import subprocess


def play_alert():
    system = platform.system()
    if system == "Windows":
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass
    elif system == "Darwin":
        subprocess.Popen(
            ["afplay", "/System/Library/Sounds/Ping.aiff"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        # Linux — prueba varios reproductores en orden
        candidates = [
            ["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"],
            ["aplay",  "/usr/share/sounds/alsa/Front_Center.wav"],
            ["paplay", "/usr/share/sounds/gnome/default/alerts/bark.ogg"],
            ["beep"],
        ]
        for cmd in candidates:
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
            except FileNotFoundError:
                continue
