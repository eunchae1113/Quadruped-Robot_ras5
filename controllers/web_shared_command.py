"""
Thread-safe shared command state for web joystick -> robot control.

This is intentionally tiny and dependency-free so it runs cleanly on Raspberry Pi.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock


@dataclass
class WebCommand:
    # Normalized joystick values in [-1.0, 1.0]
    x: float = 0.0  # left/right
    y: float = 0.0  # forward/back
    updated_at: float = 0.0


_lock = Lock()
_cmd = WebCommand(updated_at=time.time())


def set_command(x: float, y: float) -> None:
    """Update the latest joystick command (normalized floats)."""
    now = time.time()
    with _lock:
        _cmd.x = float(x)
        _cmd.y = float(y)
        _cmd.updated_at = now


def get_command(max_age_s: float = 0.5) -> WebCommand:
    """
    Get the latest command. If it's stale, return zeros.
    This provides a safety stop when the browser disconnects.
    """
    now = time.time()
    with _lock:
        age = now - _cmd.updated_at
        if age > max_age_s:
            return WebCommand(x=0.0, y=0.0, updated_at=_cmd.updated_at)
        return WebCommand(x=_cmd.x, y=_cmd.y, updated_at=_cmd.updated_at)

