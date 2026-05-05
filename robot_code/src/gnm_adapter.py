from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from action_types import CmdVel
from cmd_vel_mock import CmdVelMockConverter, stop_cmd


def _clip(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass
class GnmAdapterParams:
    deadzone_linear_x: float = 0.01
    deadzone_angular_z: float = 0.02
    smoothing_alpha: float = 0.35


class GnmWaypointAdapter:
    """Convert frozen GNM waypoint output into stable cmd_vel commands."""

    def __init__(self, params: GnmAdapterParams | None = None) -> None:
        self.params = params or GnmAdapterParams()
        self._prev_linear_x = 0.0
        self._prev_angular_z = 0.0

    def reset(self) -> None:
        self._prev_linear_x = 0.0
        self._prev_angular_z = 0.0

    def convert(self, waypoint: Any, converter: CmdVelMockConverter) -> CmdVel:
        if not isinstance(waypoint, Mapping):
            return stop_cmd()

        target_x = waypoint.get("target_x")
        target_y = waypoint.get("target_y")

        try:
            linear_x = float(target_x)
            angular_z = float(target_y)
        except (TypeError, ValueError):
            return stop_cmd()

        linear_x = _clip(linear_x, converter.max_linear_x)
        angular_z = _clip(angular_z, converter.max_angular_z)

        if abs(linear_x) < self.params.deadzone_linear_x:
            linear_x = 0.0
        if abs(angular_z) < self.params.deadzone_angular_z:
            angular_z = 0.0

        alpha = _clip_unit(float(self.params.smoothing_alpha))
        if alpha != 1.0:
            linear_x = alpha * linear_x + (1.0 - alpha) * self._prev_linear_x
            angular_z = alpha * angular_z + (1.0 - alpha) * self._prev_angular_z

        self._prev_linear_x = linear_x
        self._prev_angular_z = angular_z

        return converter.convert(
            {
                "linear_x": linear_x,
                "angular_z": angular_z,
            }
        )


_DEFAULT_GNM_ADAPTER = GnmWaypointAdapter()


def reset_default_gnm_adapter() -> None:
    _DEFAULT_GNM_ADAPTER.reset()


def gnm_waypoint_to_cmd_vel(
    waypoint: Any,
    converter: CmdVelMockConverter,
    adapter: GnmWaypointAdapter | None = None,
) -> CmdVel:
    active_adapter = adapter or _DEFAULT_GNM_ADAPTER
    return active_adapter.convert(waypoint, converter)
