from pathlib import Path

from cmd_vel_mock import CmdVelMockConverter
from gnm_adapter import gnm_waypoint_to_cmd_vel
from omnivla_adapter import omnivla_action_to_cmd_vel


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "config" / "safety_config.yaml"
    converter = CmdVelMockConverter.from_config(config_path)

    gnm_output = {"target_x": 0.25, "target_y": 0.5}
    gnm_cmd = gnm_waypoint_to_cmd_vel(gnm_output, converter)
    print("GNM mock output:", gnm_output)
    print("GNM -> CmdVel:", gnm_cmd.to_dict())

    omnivla_action = "left"
    omnivla_cmd = omnivla_action_to_cmd_vel(omnivla_action, converter)
    print("OmniVLA mock output:", omnivla_action)
    print("OmniVLA -> CmdVel:", omnivla_cmd.to_dict())

    unknown_action = "jump"
    unknown_cmd = omnivla_action_to_cmd_vel(unknown_action, converter)
    print("Unknown action:", unknown_action)
    print("Unknown -> CmdVel (safe stop):", unknown_cmd.to_dict())


if __name__ == "__main__":
    main()
