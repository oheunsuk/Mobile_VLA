from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


MAX_LINEAR_X = 0.10
MAX_ANGULAR_Z = 0.30

try:
    import torch
    from torch import nn

    _TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover - environment dependent
    torch = None  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]
    _TORCH_AVAILABLE = False


def _clip(value: float, limit: float) -> float:
    numeric = float(value)
    if numeric > limit:
        return limit
    if numeric < -limit:
        return -limit
    return numeric


class _FallbackCmdVelModel:
    """Safe fallback when torch/checkpoint is unavailable."""

    def predict_cmd_vel(self, image: Any) -> dict[str, float]:
        digest = hashlib.sha256(repr(image).encode("utf-8")).digest()
        linear_seed = (digest[0] / 255.0) * 2.0 - 1.0
        angular_seed = (digest[1] / 255.0) * 2.0 - 1.0

        linear_x = _clip(linear_seed * MAX_LINEAR_X, MAX_LINEAR_X)
        angular_z = _clip(angular_seed * MAX_ANGULAR_Z, MAX_ANGULAR_Z)
        return {"linear_x": float(linear_x), "angular_z": float(angular_z)}


if _TORCH_AVAILABLE:

    class CmdVelActionHead(nn.Module):
        def __init__(self, in_dim: int, hidden_dim: int = 64) -> None:
            super().__init__()
            self.mlp = nn.Sequential(
                nn.Linear(in_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, 2),
                nn.Tanh(),
            )

        def forward(self, features: "torch.Tensor") -> "torch.Tensor":
            return self.mlp(features)


    class GNMWithHead(nn.Module):
        def __init__(
            self,
            backbone: "nn.Module",
            feature_dim: int,
            hidden_dim: int = 64,
        ) -> None:
            super().__init__()
            self.backbone = backbone
            self.action_head = CmdVelActionHead(feature_dim, hidden_dim=hidden_dim)
            self._freeze_backbone()

        def _freeze_backbone(self) -> None:
            for param in self.backbone.parameters():
                param.requires_grad = False

        def forward(self, image_tensor: "torch.Tensor") -> "torch.Tensor":
            features = self.backbone(image_tensor)
            if features.dim() > 2:
                features = features.flatten(start_dim=1)
            return self.action_head(features)

        def predict_cmd_vel(self, image: Any) -> dict[str, float]:
            tensor = self._to_tensor(image)
            with torch.no_grad():
                output = self.forward(tensor).squeeze(0)

            linear_x = _clip(float(output[0].item()) * MAX_LINEAR_X, MAX_LINEAR_X)
            angular_z = _clip(float(output[1].item()) * MAX_ANGULAR_Z, MAX_ANGULAR_Z)
            return {"linear_x": float(linear_x), "angular_z": float(angular_z)}

        @classmethod
        def from_checkpoint(
            cls,
            checkpoint_path: str | Path,
            backbone: "nn.Module",
            feature_dim: int,
            hidden_dim: int = 64,
        ) -> "GNMWithHead":
            path = Path(checkpoint_path)
            if not path.exists():
                raise FileNotFoundError(f"Checkpoint not found: {path}")

            model = cls(backbone=backbone, feature_dim=feature_dim, hidden_dim=hidden_dim)
            state_dict = torch.load(path, map_location="cpu")
            model.load_state_dict(state_dict, strict=False)
            model.eval()
            return model

        def _to_tensor(self, image: Any) -> "torch.Tensor":
            if isinstance(image, torch.Tensor):
                tensor = image.float()
            else:
                tensor = torch.tensor(image, dtype=torch.float32)

            if tensor.dim() == 3:
                tensor = tensor.unsqueeze(0)
            elif tensor.dim() == 2:
                tensor = tensor.unsqueeze(0).unsqueeze(0)
            elif tensor.dim() == 1:
                tensor = tensor.unsqueeze(0)

            return tensor

else:

    class CmdVelActionHead:  # pragma: no cover - torch-free fallback symbol
        def __init__(self, in_dim: int, hidden_dim: int = 64) -> None:
            self.in_dim = in_dim
            self.hidden_dim = hidden_dim


    class GNMWithHead:
        def __init__(self, backbone: Any, feature_dim: int, hidden_dim: int = 64) -> None:
            self.backbone = backbone
            self.feature_dim = feature_dim
            self.hidden_dim = hidden_dim
            self._fallback = _FallbackCmdVelModel()

        def predict_cmd_vel(self, image: Any) -> dict[str, float]:
            return self._fallback.predict_cmd_vel(image)


def predict_cmd_vel(image: Any, checkpoint_path: str | Path | None = None) -> dict[str, float]:
    """Predict cmd_vel from image; fall back to a stub model when needed."""
    if not _TORCH_AVAILABLE:
        return _FallbackCmdVelModel().predict_cmd_vel(image)

    if checkpoint_path is None:
        return _FallbackCmdVelModel().predict_cmd_vel(image)

    path = Path(checkpoint_path)
    if not path.exists():
        return _FallbackCmdVelModel().predict_cmd_vel(image)

    # Lightweight default backbone for checkpoint-backed inference.
    backbone = nn.Sequential(
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Flatten(),
        nn.Linear(3, 16),
        nn.ReLU(),
        nn.Linear(16, 16),
    )
    model = GNMWithHead.from_checkpoint(path, backbone=backbone, feature_dim=16, hidden_dim=32)
    return model.predict_cmd_vel(image)

