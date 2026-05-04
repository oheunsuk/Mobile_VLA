from __future__ import annotations

from typing import Any

from action_types import CmdVel
from cmd_vel_mock import CmdVelMockConverter, stop_cmd


ACTION_TO_CMD = {
    "forward": {"linear_x": 1.0, "angular_z": 0.0},
    "backward": {"linear_x": -1.0, "angular_z": 0.0},
    "left": {"linear_x": 0.0, "angular_z": 1.0},
    "right": {"linear_x": 0.0, "angular_z": -1.0},
    "stop": {"linear_x": 0.0, "angular_z": 0.0},
}


def omnivla_action_to_cmd_vel(
    action: Any,
    converter: CmdVelMockConverter,
) -> CmdVel:
    if not isinstance(action, str):
        return stop_cmd()

    mapped = ACTION_TO_CMD.get(action.strip().lower())
    if mapped is None:
        return stop_cmd()

    return converter.convert(mapped)
