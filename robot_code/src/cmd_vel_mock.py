from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from action_types import CmdVel


DEFAULT_MAX_LINEAR_X = 0.10
DEFAULT_MAX_ANGULAR_Z = 0.30


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_safety_config(config_path: str | Path) -> Dict[str, Any]:
    path = Path(config_path)
    config: Dict[str, Any] = {
        "max_linear_x": DEFAULT_MAX_LINEAR_X,
        "max_angular_z": DEFAULT_MAX_ANGULAR_Z,
        "default_stop": True,
        "ros_publish_enabled": False,
    }

    if not path.exists():
        return config

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if key in {"max_linear_x", "max_angular_z"}:
            try:
                config[key] = float(value)
            except ValueError:
                continue
        elif key in {"default_stop", "ros_publish_enabled"}:
            config[key] = _parse_bool(value, bool(config[key]))

    return config


def clamp(value: Any, limit: float) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(-limit, min(limit, numeric))


def stop_cmd() -> CmdVel:
    return CmdVel(linear_x=0.0, angular_z=0.0)


class CmdVelMockConverter:
    def __init__(
        self,
        max_linear_x: float = DEFAULT_MAX_LINEAR_X,
        max_angular_z: float = DEFAULT_MAX_ANGULAR_Z,
    ) -> None:
        self.max_linear_x = abs(float(max_linear_x))
        self.max_angular_z = abs(float(max_angular_z))

    @classmethod
    def from_config(cls, config_path: str | Path) -> "CmdVelMockConverter":
        config = load_safety_config(config_path)
        return cls(
            max_linear_x=float(config.get("max_linear_x", DEFAULT_MAX_LINEAR_X)),
            max_angular_z=float(config.get("max_angular_z", DEFAULT_MAX_ANGULAR_Z)),
        )

    def convert(self, raw_cmd: Any) -> CmdVel:
        if isinstance(raw_cmd, CmdVel):
            linear_x = raw_cmd.linear_x
            angular_z = raw_cmd.angular_z
        elif isinstance(raw_cmd, dict):
            linear_x = raw_cmd.get("linear_x", 0.0)
            angular_z = raw_cmd.get("angular_z", 0.0)
        else:
            return stop_cmd()

        return CmdVel(
            linear_x=clamp(linear_x, self.max_linear_x),
            angular_z=clamp(angular_z, self.max_angular_z),
        )
