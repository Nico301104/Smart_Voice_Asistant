import pyttsx3
import threading

_engine = None
_lock = threading.Lock()
_callback = None


def set_callback(fn):
    global _callback
    _callback = fn


def _build_engine():
    global _engine
    if _engine is not None:
        return _engine
    _engine = pyttsx3.init()
    _engine.setProperty("rate", 160)
    _engine.setProperty("volume", 0.92)
    for v in _engine.getProperty("voices"):
        if "en" in v.id.lower():
            _engine.setProperty("voice", v.id)
            break
    return _engine


def say(text):
    print(f"[assistant] {text}")
    if _callback:
        _callback(text)
    with _lock:
        eng = _build_engine()
        eng.say(text)
        eng.runAndWait()
