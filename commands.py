import subprocess
import webbrowser
import urllib.parse
import sys

from config import APPS, SEARCH_ENGINE
from speaker import say


def _launch(name):
    candidates = APPS.get(name.lower(), [name])
    for cmd in candidates:
        try:
            if sys.platform == "win32":
                subprocess.Popen(
                    cmd if isinstance(cmd, list) else [cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                subprocess.Popen(
                    cmd if isinstance(cmd, list) else [cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return True
        except (FileNotFoundError, OSError, PermissionError):
            continue
    return False


def open_app(name):
    if _launch(name):
        say(f"Opening {name}.")
    else:
        say(f"Could not find {name}.")


def search_web(query):
    if not query:
        say("I didn't catch what to search for.")
        return
    say(f"Searching for {query}.")
    webbrowser.open(SEARCH_ENGINE + urllib.parse.quote(query))


def dispatch(text):
    words = text.split()

    if not words:
        return False

    if "open" in words:
        target = " ".join(words[words.index("open") + 1:]).strip()
        if target:
            open_app(target)
            return True

    for trigger in ("search for", "search", "look up", "find"):
        if trigger in text:
            raw = text.split(trigger, 1)[-1].strip()
            for filler in ("on the internet", "on the web", "online", "on google"):
                raw = raw.replace(filler, "").strip()
            search_web(raw)
            return True

    if any(w in text for w in ("stop", "exit", "quit", "goodbye", "bye")):
        say("Goodbye.")
        return "exit"

    return False
