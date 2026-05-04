from __future__ import annotations

from pathlib import Path

from cmd_vel_mock import CmdVelMockConverter
from gnm_adapter import gnm_waypoint_to_cmd_vel
from omnivla_adapter import omnivla_action_to_cmd_vel
from ros2_bridge_stub import Ros2BridgeStub


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "config" / "safety_config.yaml"

    converter = CmdVelMockConverter.from_config(config_path)
    bridge = Ros2BridgeStub()

    gnm_output = {"target_x": 0.2, "target_y": 0.8}
    gnm_cmd = gnm_waypoint_to_cmd_vel(gnm_output, converter)
    bridge.publish_cmd_vel(gnm_cmd, source="GNM")

    omnivla_action = "forward"
    omnivla_cmd = omnivla_action_to_cmd_vel(omnivla_action, converter)
    bridge.publish_cmd_vel(omnivla_cmd, source="OmniVLA")

    unknown_action = "spin-999"
    unknown_cmd = omnivla_action_to_cmd_vel(unknown_action, converter)
    bridge.publish_cmd_vel(unknown_cmd, source="OmniVLA-unknown")


if __name__ == "__main__":
    main()
