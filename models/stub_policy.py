from __future__ import annotations

from dataclasses import dataclass

from data.droid_contract import NormalizedDroidSample


@dataclass(frozen=True)
class StubModelOutputs:
    gnm_waypoint: dict[str, float]
    omnivla_action: str


class StubOmniVlaGnmPolicy:
    """Deterministic placeholder until real OmniVLA/GNM checkpoints are wired."""

    def predict(self, sample: NormalizedDroidSample) -> StubModelOutputs:
        action = sample.action
        return StubModelOutputs(
            gnm_waypoint={
                "target_x": action.target_linear_x,
                "target_y": action.target_angular_z,
            },
            omnivla_action=action.discrete_hint or self._infer_discrete_action(sample),
        )

    def _infer_discrete_action(self, sample: NormalizedDroidSample) -> str:
        linear_x = sample.action.target_linear_x
        angular_z = sample.action.target_angular_z

        if abs(linear_x) >= abs(angular_z):
            if linear_x > 0.01:
                return "forward"
            if linear_x < -0.01:
                return "backward"
        else:
            if angular_z > 0.01:
                return "left"
            if angular_z < -0.01:
                return "right"

        return "stop"
