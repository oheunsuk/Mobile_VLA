from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class CmdVel:
    linear_x: float
    angular_z: float

    def to_dict(self) -> dict:
        return asdict(self)
