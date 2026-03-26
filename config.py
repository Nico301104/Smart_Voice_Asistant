import os
import sys

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model")
SAMPLE_RATE = 16000
CHUNK_SIZE = 4096

_home = os.path.expanduser("~")

if sys.platform == "win32":
    APPS = {
        "browser":      [r"C:\Program Files\Google\Chrome\Application\chrome.exe"],
        "text":    ["notepad"],
        "calculator": ["calc"],
        "terminal":   ["wt", "cmd"],
        "spotify":    [os.path.join(_home, "AppData", "Roaming", "Spotify", "Spotify.exe")],
        "code":       [r"C:\Users\Nico Kiss\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code"],
        "task manager": ["taskmgr"],
    }
SEARCH_ENGINE = "https://www.google.com/search?q="

WAKE_WORDS = ["nico"]
