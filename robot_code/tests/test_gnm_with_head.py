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

from models.gnm_with_head import MAX_ANGULAR_Z, MAX_LINEAR_X, predict_cmd_vel


class TestGnmWithHead(unittest.TestCase):
    def test_predict_cmd_vel_output_type_and_range(self) -> None:
        output = predict_cmd_vel(image=[[0.1, 0.2], [0.3, 0.4]])

        self.assertIsInstance(output["linear_x"], float)
        self.assertIsInstance(output["angular_z"], float)
        self.assertLessEqual(abs(output["linear_x"]), MAX_LINEAR_X)
        self.assertLessEqual(abs(output["angular_z"]), MAX_ANGULAR_Z)

    def test_checkpoint_missing_falls_back_to_stub(self) -> None:
        output = predict_cmd_vel(image="demo-image", checkpoint_path="missing_checkpoint.pt")
        self.assertIsInstance(output["linear_x"], float)
        self.assertIsInstance(output["angular_z"], float)
        self.assertLessEqual(abs(output["linear_x"]), MAX_LINEAR_X)
        self.assertLessEqual(abs(output["angular_z"]), MAX_ANGULAR_Z)

    def test_backbone_frozen_head_trainable_when_torch_available(self) -> None:
        try:
            import torch
            from torch import nn
        except ImportError:
            self.skipTest("torch is unavailable; fallback path is already covered.")

        from models.gnm_with_head import GNMWithHead

        backbone = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(3, 8),
            nn.ReLU(),
            nn.Linear(8, 8),
        )
        model = GNMWithHead(backbone=backbone, feature_dim=8, hidden_dim=8)

        self.assertTrue(all(not p.requires_grad for p in model.backbone.parameters()))
        self.assertTrue(any(p.requires_grad for p in model.action_head.parameters()))

        image = torch.randn(1, 3, 8, 8)
        output = model.predict_cmd_vel(image)
        self.assertLessEqual(abs(output["linear_x"]), MAX_LINEAR_X)
        self.assertLessEqual(abs(output["angular_z"]), MAX_ANGULAR_Z)

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
