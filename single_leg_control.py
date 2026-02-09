"""
다리 하나만 연결된 상태에서, 그 다리 서보만 써서 테스트합니다.

  python single_leg_control.py

실행 후 → 연결된 다리 선택 (FR/FL/BR/BL) → 그 채널만 사용해서 조종.
(다른 채널은 건드리지 않음.)
  s 90   = shoulder 90°
  e 90   = elbow 90°
  h 90   = hip 90° (앞다리만)
  c      = 이 다리만 기준 캘리브 각도로
  q      = 종료
"""
from __future__ import annotations

import os
import sys

_ROOT = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# 다리별: (채널 인덱스 리스트, (이름, 채널) 리스트, 캘리브 각도)
# quadruped.py Motor 순서와 동일
LEGS = {
    "FR": {
        "channels": [0, 1, 2],
        "motors": [("shoulder", 0), ("elbow", 1), ("hip", 2)],
        "calib": [60, 90, 90],
    },
    "FL": {
        "channels": [3, 4, 5],
        "motors": [("shoulder", 3), ("elbow", 4), ("hip", 5)],
        "calib": [120, 90, 90],
    },
    "BR": {
        "channels": [6, 7],
        "motors": [("shoulder", 6), ("elbow", 7)],
        "calib": [60, 90],
    },
    "BL": {
        "channels": [8, 9],
        "motors": [("shoulder", 8), ("elbow", 9)],
        "calib": [120, 90],
    },
}


def run():
    leg = input("연결된 다리가 어느 쪽인가요? (FR / FL / BR / BL): ").strip().upper()
    if leg not in LEGS:
        print("FR, FL, BR, BL 중 하나를 입력하세요.")
        return

    info = LEGS[leg]
    channels = info["channels"]
    motors = info["motors"]
    calib = info["calib"]

    print(f"\n{leg} 다리만 사용합니다. 채널: {channels}")
    print("s 90 / e 90 / h 90 (앞다리만 h) | c=캘리브 | q=종료\n")

    try:
        from adafruit_servokit import ServoKit
    except ImportError:
        print("오류: adafruit_servokit 없음. pip install adafruit-circuitpython-servokit")
        return

    kit = ServoKit(channels=16)
    # 이 다리의 채널만 펄스 범위 설정 (다른 채널은 건드리지 않음)
    for ch in channels:
        kit.servo[ch].set_pulse_width_range(500, 2500)

    while True:
        cmd = input(f"[{leg}] ").strip().upper()
        if not cmd:
            continue
        if cmd == "Q":
            break
        if cmd == "C":
            for (name, ch), angle in zip(motors, calib):
                kit.servo[ch].angle = angle
                print(f"  {name} → {angle}°")
            continue
        parts = cmd.split()
        if len(parts) != 2:
            print("예: s 90  e 100  h 90")
            continue
        key, val = parts[0], parts[1]
        try:
            angle = int(val)
            if not 0 <= angle <= 180:
                print("각도는 0~180")
                continue
        except ValueError:
            print("각도는 숫자로")
            continue
        found = False
        for name, ch in motors:
            if name[0] == key:
                kit.servo[ch].angle = angle
                print(f"  {name} → {angle}°")
                found = True
                break
        if not found:
            print("s=shoulder, e=elbow, h=hip (FR/FL만 hip 있음)")

    print("종료.")


if __name__ == "__main__":
    run()
