from __future__ import annotations

import io
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
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
from ros2_cmdvel_publisher import Ros2CmdVelPublisher


class TestDryRunBaseline(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_path = PROJECT_ROOT / "data" / "samples" / "demo_droid_sample.json"
        self.safety_config = PROJECT_ROOT / "robot_code" / "config" / "safety_config.yaml"
        self.converter = CmdVelMockConverter.from_config(self.safety_config)

    def test_droid_sample_load(self) -> None:
        sample = load_droid_sample(self.sample_path)
        self.assertEqual(sample.episode_id, "demo_episode")
        self.assertIsInstance(sample.action.target_linear_x, float)
        self.assertIsInstance(sample.action.target_angular_z, float)

    def test_stub_policy_output(self) -> None:
        sample = demo_droid_sample()
        outputs = StubOmniVlaGnmPolicy().predict(sample)

        self.assertIn("target_x", outputs.gnm_waypoint)
        self.assertIn("target_y", outputs.gnm_waypoint)
        self.assertIsInstance(outputs.gnm_waypoint["target_x"], float)
        self.assertIsInstance(outputs.gnm_waypoint["target_y"], float)
        self.assertIn(outputs.omnivla_action, {"forward", "backward", "left", "right", "stop"})

    def test_cmd_vel_conversion(self) -> None:
        sample = load_droid_sample(self.sample_path)
        outputs = StubOmniVlaGnmPolicy().predict(sample)

        gnm_cmd = gnm_waypoint_to_cmd_vel(outputs.gnm_waypoint, self.converter)
        omnivla_cmd = omnivla_action_to_cmd_vel(outputs.omnivla_action, self.converter)

        self.assertIsInstance(gnm_cmd.linear_x, float)
        self.assertIsInstance(gnm_cmd.angular_z, float)
        self.assertIsInstance(omnivla_cmd.linear_x, float)
        self.assertIsInstance(omnivla_cmd.angular_z, float)
        self.assertLessEqual(abs(gnm_cmd.linear_x), self.converter.max_linear_x)
        self.assertLessEqual(abs(gnm_cmd.angular_z), self.converter.max_angular_z)

    def test_ros_publish_disabled_stays_dry_run(self) -> None:
        publisher = Ros2CmdVelPublisher(ros_publish_enabled=False)
        cmd = self.converter.convert({"linear_x": 0.05, "angular_z": 0.01})

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            publisher.publish(cmd)

        output = output_buffer.getvalue()
        self.assertIn("[DRY RUN]", output)
        self.assertIsNone(publisher._rclpy)

    def test_cli_command_runs(self) -> None:
        command = [
            sys.executable,
            "scripts/run_droid_offline_dry.py",
            "--sample",
            "data/samples/demo_droid_sample.json",
        ]
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("[DROID SAMPLE]", result.stdout)
        self.assertIn("GNM-from-DROID", result.stdout)
        self.assertIn("OmniVLA-from-DROID", result.stdout)


if __name__ == "__main__":
    unittest.main()
