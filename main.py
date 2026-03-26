import threading
import sys

from core import AssistantCore


def main():
    stop = threading.Event()

    def on_state(s):
        print(f"[state] {s}")

    def on_log(role, text):
        prefix = {"user": "you", "assistant": "nico", "system": "sys"}.get(role, role)
        print(f"[{prefix}] {text}")

    core = AssistantCore(on_state=on_state, on_log=on_log)
    core.start()

    try:
        stop.wait()
    except KeyboardInterrupt:
        core.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
