import json
import queue
import threading

import vosk
import sounddevice as sd

from config import MODEL_PATH, SAMPLE_RATE, CHUNK_SIZE

_model = None
_model_lock = threading.Lock()


def _get_model():
    global _model
    with _model_lock:
        if _model is None:
            print("[*] Loading speech model...")
            _model = vosk.Model(MODEL_PATH)
            print("[*] Model ready.")
    return _model


def transcribe_once(timeout=7):
    model = _get_model()
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    buf = queue.Queue()

    def _cb(indata, frames, t, status):
        buf.put(bytes(indata))

    text = ""
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK_SIZE,
                            dtype="int16", channels=1, callback=_cb):
        sd.sleep(int(timeout * 1000))

    while not buf.empty():
        if rec.AcceptWaveform(buf.get()):
            text += " " + json.loads(rec.Result()).get("text", "")

    text += " " + json.loads(rec.FinalResult()).get("text", "")
    return text.strip().lower()


def stream(on_text, stop_event):
    model = _get_model()
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    buf = queue.Queue()

    def _cb(indata, frames, t, status):
        buf.put(bytes(indata))

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=CHUNK_SIZE,
                            dtype="int16", channels=1, callback=_cb):
        while not stop_event.is_set():
            try:
                data = buf.get(timeout=1)
            except queue.Empty:
                continue
            if rec.AcceptWaveform(data):
                word = json.loads(rec.Result()).get("text", "").strip().lower()
                if word:
                    on_text(word)
