# Repository Structure

This repository is organized so training/data work can happen on a development
machine, while robot execution stays isolated under `robot_code/`.

## Top-level Layout

- `data/`: DROID sample contract and small normalized demo samples. Raw DROID
  data should stay outside git and be referenced by config paths.
- `models/`: OmniVLA/GNM model interfaces. The current implementation is a
  deterministic stub that preserves the future checkpoint output contract.
- `training/`: Reserved for DROID preprocessing and training entrypoints.
- `inference/`: Reserved for checkpoint loading and runtime inference modules.
- `configs/`: Pipeline-level config paths for data, model, and robot settings.
- `scripts/`: Local development and dry-run commands.
- `robot_code/`: Robot-facing conversion, safety limits, and ROS2 bridge code.

## Current Offline Flow

```text
DROID JSON sample
  -> NormalizedDroidSample
  -> StubOmniVlaGnmPolicy
  -> GNM waypoint + OmniVLA action
  -> CmdVelMockConverter
  -> Ros2BridgeStub dry-run logs
```

Run the dry flow with:

```bash
python scripts/run_droid_offline_dry.py --sample data/samples/demo_droid_sample.json
```

On the robot PC, keep `ros_publish_enabled` disabled until the dry output is
verified against the real robot's expected `/cmd_vel` limits.
