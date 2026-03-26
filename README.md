# 🎙️ Nico — Offline Voice Assistant

Nico is a lightweight offline voice assistant built in Python. It listens for a wake word, processes voice commands locally, and executes actions without relying on cloud services.

---

## 🚀 Features

* Offline speech recognition (Vosk)
* Wake word detection (`nico`)
* Launch desktop applications
* Perform web searches
* Optional GUI interface
* Fast and lightweight

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Nico301104/Smart_Voice_Asistant.git
cd Smart_Voice_Asistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🧠 Speech Model Setup

Download a Vosk model:
https://alphacephei.com/vosk/models

Recommended:

```
vosk-model-small-en-us-0.15
```

Extract it like this:

```
nico/
├── model/
```

---

## ▶️ Run

### With GUI

```bash
python gui.py
```

### Without GUI

```bash
python main.py
```

---

## 🎯 Wake Word

```
nico
```

---

## 🗂️ Project Structure

```
nico/
├── model/
├── config.py
├── listener.py
├── speaker.py
├── commands.py
├── core.py
├── gui.py
├── main.py
└── requirements.txt
```

---

## 🧩 Commands

| Command                  | Action          |
| ------------------------ | --------------- |
| `open chrome`            | Launches Chrome |
| `open terminal`          | Opens terminal  |
| `search for <query>`     | Google search   |
| `look up the weather`    | Weather search  |
| `stop` / `quit` / `exit` | Stop assistant  |

---

## ⚙️ Add Custom Apps

Edit `config.py`:

```python
APPS = {
    "vlc": ["vlc"],
    "slack": ["slack"],
}
```

---

## 🛠️ Tech Stack

* Python
* Vosk
* Tkinter

---

## 📌 Notes

* Works offline (except web searches)
* Designed for Windows
* Requires microphone access

---
## Autor
* Sandru Nicolae-Andrei
