import threading

from config import WAKE_WORDS
from speaker import say, set_callback
from commands import dispatch
from listener import stream


class AssistantCore:
    def __init__(self, on_state=None, on_log=None):
        self._on_state = on_state or (lambda s: None)
        self._on_log = on_log or (lambda r, t: None)
        self._stop = threading.Event()
        self._waiting = False
        self._thread = None
        set_callback(lambda t: self._on_log("assistant", t))

    def start(self):
        self._stop.clear()
        self._waiting = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._on_log("system", "assistant started")
        threading.Thread(target=lambda: say("Voice assistant is ready."), daemon=True).start()

    def stop(self):
        self._stop.set()
        self._waiting = False
        self._on_state("idle")
        self._on_log("system", "assistant stopped")
        threading.Thread(target=lambda: say("Goodbye."), daemon=True).start()

    def _run(self):
        self._on_state("idle")
        try:
            stream(self._handle, self._stop)
        except Exception as exc:
            self._on_log("system", f"error: {exc}")
        self._on_state("idle")

    def _handle(self, text):
        if not text:
            return

        if self._waiting:
            self._waiting = False
            self._on_log("user", text)
            self._on_state("processing")

            def run():
                result = dispatch(text)
                if result == "exit":
                    self._stop.set()
                    self._on_state("idle")
                elif not result:
                    say("I didn't understand that command.")
                self._on_state("idle")

            threading.Thread(target=run, daemon=True).start()
            return

        for w in WAKE_WORDS:
            if w in text:
                self._on_log("user", text)
                self._waiting = True
                self._on_state("wake")
                threading.Thread(target=lambda: say("Yes, listening."), daemon=True).start()

                def _timeout():
                    import time
                    time.sleep(7)
                    if self._waiting:
                        self._waiting = False
                        say("Timed out, try again.")
                        self._on_state("idle")

                threading.Thread(target=_timeout, daemon=True).start()
                return
