from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROBOT_SRC = PROJECT_ROOT / "robot_code" / "src"

for import_path in (PROJECT_ROOT, ROBOT_SRC):
    path_text = str(import_path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)

from cmd_vel_mock import CmdVelMockConverter
from data.droid_contract import demo_droid_sample, load_droid_sample
from gnm_adapter import gnm_waypoint_to_cmd_vel
from models.stub_policy import StubOmniVlaGnmPolicy
from omnivla_adapter import omnivla_action_to_cmd_vel
from ros2_bridge_stub import Ros2BridgeStub


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one normalized DROID sample through the dry OmniVLA/GNM pipeline."
    )
    parser.add_argument(
        "--sample",
        type=Path,
        default=None,
        help="Path to a normalized DROID sample JSON. Uses an embedded demo if omitted.",
    )
    parser.add_argument(
        "--safety-config",
        type=Path,
        default=PROJECT_ROOT / "robot_code" / "config" / "safety_config.yaml",
        help="Path to safety_config.yaml.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample = load_droid_sample(args.sample) if args.sample else demo_droid_sample()

    policy = StubOmniVlaGnmPolicy()
    outputs = policy.predict(sample)

    converter = CmdVelMockConverter.from_config(args.safety_config)
    bridge = Ros2BridgeStub()

    print(
        "[DROID SAMPLE]",
        {
            "episode_id": sample.episode_id,
            "step_index": sample.step_index,
            "language_instruction": sample.observation.language_instruction,
            "goal": sample.goal,
        },
    )

    gnm_cmd = gnm_waypoint_to_cmd_vel(outputs.gnm_waypoint, converter)
    bridge.publish_cmd_vel(gnm_cmd, source="GNM-from-DROID")

    omnivla_cmd = omnivla_action_to_cmd_vel(outputs.omnivla_action, converter)
    bridge.publish_cmd_vel(omnivla_cmd, source="OmniVLA-from-DROID")


if __name__ == "__main__":
    main()
