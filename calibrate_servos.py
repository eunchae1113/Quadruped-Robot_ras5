"""
서보모터 캘리브레이션 — 제작/조립 시 기준 각도로 모든 서보를 맞춥니다.

  python calibrate_servos.py          → quadruped 기준 중립각도 적용
  python calibrate_servos.py 90      → 모든 서보 90도로 통일 (중립 테스트용)

라즈베리파이에서 실행 시: sudo 또는 I2C 권한 확인.
"""
from __future__ import annotations

import os
import sys

_ROOT = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# 채널별 이름 (quadruped.py Motor enum 순서)
SERVO_NAMES = [
    "FR_SHOULDER", "FR_ELBOW", "FR_HIP",   # 0,1,2
    "FL_SHOULDER", "FL_ELBOW", "FL_HIP",   # 3,4,5
    "BR_SHOULDER", "BR_ELBOW",             # 6,7
    "BL_SHOULDER", "BL_ELBOW",             # 8,9
]

# quadruped.calibrate() 와 동일한 중립각 (제작용 기준)
DEFAULT_CALIBRATION = {
    0: 60,   # FR_SHOULDER
    1: 90,   # FR_ELBOW
    2: 90,   # FR_HIP
    3: 120,  # FL_SHOULDER
    4: 90,   # FL_ELBOW
    5: 90,   # FL_HIP
    6: 60,   # BR_SHOULDER
    7: 90,   # BR_ELBOW
    8: 120,  # BL_SHOULDER
    9: 90,   # BL_ELBOW
}


def main():
    # 모든 서보를 한 각도로 맞출지 (예: 90)
    if len(sys.argv) > 1:
        try:
            one_angle = int(sys.argv[1])
        except ValueError:
            one_angle = None
        if one_angle is not None and 0 <= one_angle <= 180:
            angles = {i: one_angle for i in range(10)}
            print(f"[캘리브레이션] 모든 서보 → {one_angle}°")
        else:
            angles = DEFAULT_CALIBRATION
            print("[캘리브레이션] quadruped 기준각 적용 (인자 무시)")
    else:
        angles = DEFAULT_CALIBRATION
        print("[캘리브레이션] quadruped 기준각 적용")

    try:
        from adafruit_servokit import ServoKit
    except ImportError as e:
        print("오류: adafruit_servokit 없음. pip install adafruit-circuitpython-servokit")
        sys.exit(1)

    kit = ServoKit(channels=16)
    for i in range(10):
        kit.servo[i].set_pulse_width_range(500, 2500)
        kit.servo[i].angle = angles[i]
        print(f"  [{i}] {SERVO_NAMES[i]:12} = {angles[i]}°")

    print("완료. 다리 부착 시 이 각도를 기준으로 맞추면 됩니다.")


if __name__ == "__main__":
    main()
