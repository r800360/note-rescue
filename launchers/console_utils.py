"""Attach a visible console when launched via pythonw (taskbar shortcuts)."""
from __future__ import annotations

import os
import sys


def _enable_vt_processing() -> None:
    import ctypes

    kernel32 = ctypes.windll.kernel32
    enable_vt = 0x0004
    for handle_id in (-11, -12):  # stdout, stderr
        handle = kernel32.GetStdHandle(handle_id)
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | enable_vt)


def attach_console(title: str) -> None:
    if sys.platform != "win32":
        return

    import ctypes

    ctypes.windll.kernel32.AllocConsole()
    ctypes.windll.kernel32.SetConsoleTitleW(title)

    sys.stdin = open("CONIN$", "r", encoding="utf-8", errors="replace")
    sys.stdout = open("CONOUT$", "w", encoding="utf-8", errors="replace")
    sys.stderr = open("CONOUT$", "w", encoding="utf-8", errors="replace")

    _enable_vt_processing()
    os.environ["NOTE_RESCUE_LAUNCHER"] = "1"


def pause(message: str = "Press Enter to close...") -> None:
    try:
        input(f"\n{message}")
    except (EOFError, KeyboardInterrupt):
        pass
