from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


NumberMap = dict[str, float]


@dataclass(frozen=True)
class DroidObservation:
    image_path: str | None
    language_instruction: str
    proprioception: NumberMap = field(default_factory=dict)
    timestamp: float | None = None


@dataclass(frozen=True)
class DroidAction:
    target_linear_x: float = 0.0
    target_angular_z: float = 0.0
    discrete_hint: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedDroidSample:
    episode_id: str
    step_index: int
    observation: DroidObservation
    action: DroidAction
    goal: str | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "NormalizedDroidSample":
        observation = _as_mapping(payload.get("observation"))
        action = _as_mapping(payload.get("action"))

        return cls(
            episode_id=str(payload.get("episode_id", "unknown_episode")),
            step_index=_to_int(payload.get("step_index"), default=0),
            observation=DroidObservation(
                image_path=_first_string(
                    observation,
                    [
                        "image_path",
                        "rgb_path",
                        "exterior_image_1_left",
                        "wrist_image_left",
                    ],
                ),
                language_instruction=str(
                    observation.get(
                        "language_instruction",
                        payload.get("language_instruction", ""),
                    )
                ),
                proprioception=_number_map(
                    observation.get("proprioception", payload.get("proprioception", {}))
                ),
                timestamp=_optional_float(
                    observation.get("timestamp", payload.get("timestamp"))
                ),
            ),
            action=DroidAction(
                target_linear_x=_first_float(
                    action,
                    ["target_linear_x", "linear_x", "x", "base_linear_velocity"],
                ),
                target_angular_z=_first_float(
                    action,
                    ["target_angular_z", "angular_z", "yaw", "base_angular_velocity"],
                ),
                discrete_hint=_optional_string(
                    action.get("discrete_hint", action.get("action_label"))
                ),
                raw=dict(action),
            ),
            goal=_optional_string(payload.get("goal")),
        )


def load_droid_sample(path: str | Path) -> NormalizedDroidSample:
    sample_path = Path(path)
    with sample_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, Mapping):
        raise ValueError("DROID sample JSON must contain an object at the root.")
    return NormalizedDroidSample.from_mapping(payload)


def demo_droid_sample() -> NormalizedDroidSample:
    payload = {
        "episode_id": "demo_episode",
        "step_index": 0,
        "goal": "move toward the target",
        "observation": {
            "image_path": None,
            "language_instruction": "move forward slowly",
            "proprioception": {"base_x": 0.0, "base_yaw": 0.0},
            "timestamp": 0.0,
        },
        "action": {
            "target_linear_x": 0.08,
            "target_angular_z": 0.02,
            "discrete_hint": "forward",
        },
    }

    # Prefer loading the tracked demo JSON so CLI dry-runs and code share one baseline.
    demo_json_path = Path(__file__).resolve().parent / "samples" / "demo_droid_sample.json"
    if demo_json_path.exists():
        try:
            with demo_json_path.open("r", encoding="utf-8") as handle:
                json_payload = json.load(handle)
            if isinstance(json_payload, Mapping):
                payload = dict(json_payload)
        except (OSError, json.JSONDecodeError):
            # Keep a safe in-code fallback for malformed or unreadable demo files.
            pass

    sample = NormalizedDroidSample.from_mapping(payload)
    return NormalizedDroidSample(
        episode_id=sample.episode_id,
        step_index=sample.step_index,
        observation=sample.observation,
        action=DroidAction(
            target_linear_x=float(sample.action.target_linear_x),
            target_angular_z=float(sample.action.target_angular_z),
            discrete_hint=sample.action.discrete_hint,
            raw=sample.action.raw,
        ),
        goal=sample.goal,
    )


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _first_string(mapping: Mapping[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        value = _optional_string(mapping.get(key))
        if value is not None:
            return value
    return None


def _first_float(mapping: Mapping[str, Any], keys: list[str]) -> float:
    for key in keys:
        value = _optional_float(mapping.get(key))
        if value is not None:
            return value
    return 0.0


def _number_map(value: Any) -> NumberMap:
    if not isinstance(value, Mapping):
        return {}

    numbers: NumberMap = {}
    for key, raw_value in value.items():
        converted = _optional_float(raw_value)
        if converted is not None:
            numbers[str(key)] = converted
    return numbers
