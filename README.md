# Nico — Offline Voice Assistant

## Requirements

```
pip install -r requirements.txt
```

Download a Vosk model from https://alphacephei.com/vosk/models  
Extract it into a folder named `model/` next to the project files.

Recommended: `vosk-model-small-en-us-0.15`

```
nico/
├── model/          ← extracted vosk model goes here
├── config.py
├── listener.py
├── speaker.py
├── commands.py
├── core.py
├── gui.py
├── main.py
└── requirements.txt
```

## Run

With GUI:
```
python gui.py
```

Without GUI (terminal):
```
python main.py
```

## Wake words

`nico` 

## Commands

| Say | Action |
|-----|--------|
| `open chrome` | launches Chrome |
| `open terminal` | launches terminal |
| `search for python tutorials` | opens Google search |
| `look up the weather` | opens Google search |
| `stop` / `quit` / `exit` | shuts down |

## Adding apps

Edit `APPS` in `config.py`:

```python
APPS = {
    "vlc":  ["vlc"],
    "slack": ["slack"],
}
```
