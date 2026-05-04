#!/bin/zsh

# 1. ROS2 Humble 환경 불러오기
if [ -f "/opt/ros/humble/setup.zsh" ]; then
    source /opt/ros/humble/setup.zsh
else
    echo "ROS2 Humble setup.zsh를 찾을 수 없습니다."
fi

# 2. SerBot 테스트 통신 채널 설정
export ROS_DOMAIN_ID=10

# 3. 내 테스트 workspace가 있으면 불러오기
if [ -f "$HOME/serbot_test/install/setup.zsh" ]; then
    source "$HOME/serbot_test/install/setup.zsh"
fi

# 4. 가상환경 활성화
if [ -d "$HOME/serbot_test/venv" ]; then
    source "$HOME/serbot_test/venv/bin/activate"
    VENV_STATUS="venv 활성화됨"
else
    VENV_STATUS="venv 없음"
fi

echo "SerBot test environment ready"
echo "현재 폴더: $(pwd)"
echo "ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "Python: $(which python)"
echo "가상환경 상태: $VENV_STATUS"