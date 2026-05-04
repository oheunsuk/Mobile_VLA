# SerBot II Robot Part Mock Interface Summary

## Purpose

This structure is a safe mock interface for the SerBot II robot part.
It does not publish ROS messages and does not control a real robot.
The goal is to prepare a clean conversion layer that can be connected to ROS2 `/cmd_vel` later.

## Data Flow

- GNM output (assumed waypoint): `target_x`, `target_y`
- `gnm_adapter.py`
- `CmdVelMockConverter` in `cmd_vel_mock.py`
- `CmdVel` object (mock-safe command)

and

- OmniVLA output (assumed discrete action): `forward`, `backward`, `left`, `right`, `stop`
- `omnivla_adapter.py`
- `CmdVelMockConverter` in `cmd_vel_mock.py`
- `CmdVel` object (mock-safe command)

## Safety Characteristics

- No ROS imports (`rclpy`, `geometry_msgs`) are used.
- No `/cmd_vel` publish is executed.
- Unknown inputs/actions are converted to a safe stop command.
- Velocity values are clamped with configured limits from `config/safety_config.yaml`.
