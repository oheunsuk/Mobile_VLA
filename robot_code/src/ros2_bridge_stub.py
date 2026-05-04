from __future__ import annotations

from action_types import CmdVel


class Ros2BridgeStub:
    """Dry-run bridge that only logs CmdVel values."""

    def publish_cmd_vel(self, cmd: CmdVel, source: str = "unknown") -> None:
        print(f"[DRY RUN] source={source} cmd_vel={cmd.to_dict()}")
