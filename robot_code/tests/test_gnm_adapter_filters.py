from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROBOT_SRC = PROJECT_ROOT / "robot_code" / "src"

for import_path in (PROJECT_ROOT, ROBOT_SRC):
    path_text = str(import_path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)

from cmd_vel_mock import CmdVelMockConverter
from gnm_adapter import GnmAdapterParams, GnmWaypointAdapter


class TestGnmAdapterFilters(unittest.TestCase):
    def setUp(self) -> None:
        safety_config = PROJECT_ROOT / "robot_code" / "config" / "safety_config.yaml"
        self.converter = CmdVelMockConverter.from_config(safety_config)

    def test_deadzone_applies(self) -> None:
        adapter = GnmWaypointAdapter(
            GnmAdapterParams(deadzone_linear_x=0.05, deadzone_angular_z=0.05, smoothing_alpha=1.0)
        )
        cmd = adapter.convert({"target_x": 0.01, "target_y": -0.02}, self.converter)
        self.assertEqual(cmd.linear_x, 0.0)
        self.assertEqual(cmd.angular_z, 0.0)

    def test_smoothing_applies(self) -> None:
        adapter = GnmWaypointAdapter(
            GnmAdapterParams(deadzone_linear_x=0.0, deadzone_angular_z=0.0, smoothing_alpha=0.5)
        )
        cmd_1 = adapter.convert({"target_x": 0.10, "target_y": 0.30}, self.converter)
        cmd_2 = adapter.convert({"target_x": 0.10, "target_y": 0.30}, self.converter)

        self.assertAlmostEqual(cmd_1.linear_x, 0.05, places=6)
        self.assertAlmostEqual(cmd_1.angular_z, 0.15, places=6)
        self.assertAlmostEqual(cmd_2.linear_x, 0.075, places=6)
        self.assertAlmostEqual(cmd_2.angular_z, 0.225, places=6)

    def test_clamp_range_applies(self) -> None:
        adapter = GnmWaypointAdapter(
            GnmAdapterParams(deadzone_linear_x=0.0, deadzone_angular_z=0.0, smoothing_alpha=1.0)
        )
        cmd = adapter.convert({"target_x": 10.0, "target_y": -10.0}, self.converter)

        self.assertIsInstance(cmd.linear_x, float)
        self.assertIsInstance(cmd.angular_z, float)
        self.assertLessEqual(abs(cmd.linear_x), 0.10)
        self.assertLessEqual(abs(cmd.angular_z), 0.30)

    def test_dry_run_command_still_passes(self) -> None:
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
        self.assertIn("[DRY RUN]", result.stdout)


if __name__ == "__main__":
    unittest.main()
