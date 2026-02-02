"""
Controller adapter for gait_logic.quadruped.Quadruped.move().

The original project supports different controllers (keyboard/network).
This controller injects joystick (x,y) coming from the Flask web UI.
"""

from __future__ import annotations

import numpy as np

from controllers.web_shared_command import get_command


def controller(momentum, accel: float = 0.25, bound: float = 4.0):
    """
    Map web joystick values to the robot's momentum vector.

    Existing code expects:
      momentum = np.asarray([x, z, scale, close], dtype=np.float32)

    We'll interpret:
      - web y (forward/back) -> momentum[0]
      - web x (left/right)   -> momentum[1]

    The web UI posts stickX/stickY in roughly [-1, 1].
    """
    if not isinstance(momentum, np.ndarray):
        momentum = np.asarray(momentum, dtype=np.float32)

    cmd = get_command(max_age_s=0.5)

    target_x = float(cmd.y) * bound
    target_z = float(cmd.x) * bound

    # Smooth acceleration toward target for stability.
    momentum[0] = float(np.clip(momentum[0] + np.clip(target_x - momentum[0], -accel, accel), -bound, bound))
    momentum[1] = float(np.clip(momentum[1] + np.clip(target_z - momentum[1], -accel, accel), -bound, bound))

    # Keep stride/scale enabled and do not request close.
    if momentum.shape[0] >= 3:
        momentum[2] = 1.0
    if momentum.shape[0] >= 4:
        momentum[3] = 0.0

    return momentum.astype(np.float32, copy=False)

