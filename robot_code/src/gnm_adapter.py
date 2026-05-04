from __future__ import annotations

from typing import Any, Mapping

from action_types import CmdVel
from cmd_vel_mock import CmdVelMockConverter, stop_cmd


def gnm_waypoint_to_cmd_vel(
    waypoint: Any,
    converter: CmdVelMockConverter,
) -> CmdVel:
    if not isinstance(waypoint, Mapping):
        return stop_cmd()

    target_x = waypoint.get("target_x")
    target_y = waypoint.get("target_y")

    try:
        raw_linear_x = float(target_x)
        raw_angular_z = float(target_y)
    except (TypeError, ValueError):
        return stop_cmd()

    return converter.convert(
        {
            "linear_x": raw_linear_x,
            "angular_z": raw_angular_z,
        }
    )
