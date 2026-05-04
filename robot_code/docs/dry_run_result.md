# Dry Run Result

`run_pipeline_dry.py` 실행 결과, GNM/OmniVLA 입력이 `CmdVel` 형태로 변환되어 `[DRY RUN]` 로그로 출력되는 것을 확인했다.

- 실제 ROS publish 동작은 없다.
- `rclpy` import는 없다.
- unknown action 입력은 안전하게 stop(`linear_x=0.0`, `angular_z=0.0`)으로 처리됨을 확인했다.
