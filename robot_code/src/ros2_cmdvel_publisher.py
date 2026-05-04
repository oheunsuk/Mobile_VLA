from __future__ import annotations

from action_types import CmdVel


class Ros2CmdVelPublisher:
    def __init__(
        self,
        ros_publish_enabled: bool = False,
        topic: str = "/cmd_vel",
        node_name: str = "omnivla_gnm_cmdvel_publisher",
    ) -> None:
        self.ros_publish_enabled = ros_publish_enabled
        self.topic = topic
        self.node_name = node_name
        self._rclpy = None
        self._node = None
        self._publisher = None

        if self.ros_publish_enabled:
            self._initialize_ros()

    def publish(self, cmd: CmdVel) -> None:
        if not self.ros_publish_enabled:
            print("[DRY RUN]", cmd.to_dict())
            return

        twist = self._to_twist(cmd)
        self._publisher.publish(twist)

    def shutdown(self) -> None:
        if self._rclpy is None:
            return
        if self._node is not None:
            self._node.destroy_node()
        self._rclpy.shutdown()

    def _initialize_ros(self) -> None:
        try:
            import rclpy
            from geometry_msgs.msg import Twist
        except ImportError as exc:
            raise RuntimeError(
                "ROS publish is enabled, but ROS2 Python packages are not available. "
                "Run this on the robot PC after sourcing the ROS2 environment."
            ) from exc

        if not rclpy.ok():
            rclpy.init()

        self._rclpy = rclpy
        self._twist_type = Twist
        self._node = rclpy.create_node(self.node_name)
        self._publisher = self._node.create_publisher(Twist, self.topic, 10)

    def _to_twist(self, cmd: CmdVel):
        twist = self._twist_type()
        twist.linear.x = float(cmd.linear_x)
        twist.angular.z = float(cmd.angular_z)
        return twist
