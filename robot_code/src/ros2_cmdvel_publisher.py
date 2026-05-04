from __future__ import annotations

from action_types import CmdVel

# NOTE:
# rclpy import is intentionally not executed in this stage.
# It can be safely added later when real ROS2 integration is required.
try:
    # import rclpy  # Reserved for future ROS2 integration.
    pass
except Exception:
    pass


class Ros2CmdVelPublisher:
    def __init__(self, ros_publish_enabled: bool = False) -> None:
        self.ros_publish_enabled = ros_publish_enabled

    def publish(self, cmd: CmdVel) -> None:
        if not self.ros_publish_enabled:
            print("[DRY RUN]", cmd.to_dict())
            return

        # TODO: 여기에 ROS publish 들어갈 예정
        print("[DRY RUN]", cmd.to_dict())
