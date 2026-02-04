

from __future__ import annotations

import os
import sys
import threading

_ROOT = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _import_web_app():
    web_dir = os.path.join(_ROOT, "web_interface")
    if web_dir not in sys.path:
        sys.path.insert(0, web_dir)
    # Import after sys.path tweak so `from picamera2_stream import ...` works.
    import app as web_app_module  # type: ignore
    return web_app_module


def _robot_loop():
    # Import inside thread so Flask import issues don't block robot thread startup (and vice-versa).
    from gait_logic.quadruped import Quadruped
    from controllers.web_joystick_controller import controller as web_controller

    print("[robot] starting quadruped init...")

    try:
        r = Quadruped()
    except Exception as ex:
        # On Raspberry Pi, ServoKit/I2C issues are common; fail loudly with a clear error.
        print(f"[robot] failed to initialise hardware (ServoKit/I2C). Error: {repr(ex)}")
        print("[robot] check: i2c enabled, correct address, and `adafruit-circuitpython-servokit` installed.")
        return

    try:
        r.calibrate()
    except Exception as ex:
        print(f"[robot] calibrate failed: {repr(ex)}")
        return

    print("[robot] ready. waiting for web joystick commands...")

    # This call blocks forever; it will continuously poll the injected web controller.
    r.move(web_controller)


def main():
    web_app_module = _import_web_app()
    flask_app = web_app_module.app

    # Start robot control loop in separate thread
    t = threading.Thread(target=_robot_loop, daemon=True)
    t.start()

    # Run Flask server in main thread
    port = int(flask_app.config.get("APP_PORT", 5000))
    debug = bool(flask_app.config.get("APP_DEBUG", False))

    print(f"[web] starting server on 0.0.0.0:{port} (debug={debug})")

    # Use waitress in production mode (as original project does)
    if not debug:
        try:
            from waitress import serve
            serve(flask_app, host="0.0.0.0", port=port)
            return
        except Exception as ex:
            print(f"[web] waitress start failed ({repr(ex)}), falling back to Flask dev server.")

    flask_app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    main()
