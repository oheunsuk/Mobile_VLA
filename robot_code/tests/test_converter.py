from pathlib import Path
import unittest

from cmd_vel_mock import CmdVelMockConverter, clamp
from omnivla_adapter import omnivla_action_to_cmd_vel


class TestConverter(unittest.TestCase):
    def setUp(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        config_path = project_root / "config" / "safety_config.yaml"
        self.converter = CmdVelMockConverter.from_config(config_path)

    def test_clamp_behavior(self) -> None:
        self.assertEqual(clamp(0.5, 0.1), 0.1)
        self.assertEqual(clamp(-0.5, 0.1), -0.1)
        self.assertEqual(clamp("invalid", 0.1), 0.0)

    def test_unknown_action_defaults_to_stop(self) -> None:
        cmd = omnivla_action_to_cmd_vel("unknown-action", self.converter)
        self.assertEqual(cmd.linear_x, 0.0)
        self.assertEqual(cmd.angular_z, 0.0)

    def test_speed_limit_applies(self) -> None:
        cmd = self.converter.convert({"linear_x": 1.5, "angular_z": -2.0})
        self.assertEqual(cmd.linear_x, self.converter.max_linear_x)
        self.assertEqual(cmd.angular_z, -self.converter.max_angular_z)


if __name__ == "__main__":
    unittest.main()
