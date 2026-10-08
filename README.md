# Keero - Emotional AI Pet Robot 🤖

Keero is an interactive emotional AI pet robot powered by local LLMs via Ollama, speech-to-text with Google Speech Recognition, neural text-to-speech with Microsoft Edge TTS, real-time waveform visualization, and serial communication with microcontroller-based hardware (Arduino / ESP32).

---

## 📋 Table of Contents
- [Project Architecture](#project-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Hardware Protocol](#hardware-protocol)
- [Troubleshooting](#troubleshooting)

---

## 🛠 Project Architecture

- **`server.py`**: Flask web server hosting the frontend interface and exposing `/status` polling endpoint.
- **`Keero.py`**: Asynchronous brain containing:
  - **Speech Listener (`listen_worker`)**: Captures microphone input and converts speech to text.
  - **LLM Reasoning (`process_queries` & `ask_llm`)**: Sends prompts to a local Ollama instance (`mistral:7b`) and detects emotional state (`HAPPY`, `ANGRY`, `SAD`, `CONFUSED`, `NEUTRAL`).
  - **Serial Control**: Sends wake and emotion trigger signals over USB serial to the physical robot.
  - **Text-to-Speech (`tts_worker`)**: Converts generated responses into lifelike voice output using `edge-tts` and plays it via `pygame`.
- **`templates/index.html` & `static/`**: Interactive UI with real-time dynamic SiriWave visualization and chat log.

---

## ⚙ Prerequisites

1. **Python 3.10+** (Tested on Python 3.11)
2. **Microphone**: Working audio input device.
3. **Ollama**: Download and install from [ollama.com](https://ollama.com/).
   - Pull the model used by Keero:
     ```bash
     ollama pull mistral:7b
     ```
4. **Robot Hardware (Optional)**:
   - Arduino / ESP32 connected via USB Serial (Default: `COM7`, `115200` baud).
   - If not connected, Keero will automatically fall back to simulation mode without crashing.

---

## 📦 Installation

1. Clone or open the repository:
   ```bash
   cd Keero-pet-robot
   ```

2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Windows (CMD):
   .\venv\Scripts\activate.bat
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

> **Note on PyAudio**: `PyAudio` is required by `SpeechRecognition` to access your microphone. If installation fails on Windows, install the prebuilt wheel with `pip install pyaudio`.

---

## 🔧 Configuration

In [`Keero.py`](Keero.py), you can adjust the following settings near the top:

```python
# LLM model name in Ollama
MODEL = "mistral:7b"

# Serial port for Arduino / ESP32 microcontroller
SERIAL_PORT = "COM7"
BAUD_RATE = 115200
```

- Change `SERIAL_PORT` to match your device (e.g., `COM3`, `COM4` on Windows, or `/dev/ttyUSB0` on Linux).
- You can change `MODEL` to any installed Ollama model (e.g., `llama3.2`, `phi3`, etc.).

---

## 🚀 Running the Project

### Step 1: Start Ollama
Ensure the Ollama service is running:
```bash
ollama serve
```

### Step 2: Start the Keero Server & Brain
In a separate terminal, run:
```bash
python server.py
```

### Step 3: Open the Web UI
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

- Click the center microphone button to start interaction.
- Speak into your microphone. Keero will transcribe your speech, query the LLM, express the classified emotion to the robot hardware, and speak back with synthesized audio.

---

## 🔌 Hardware Protocol

Keero communicates with microcontrollers using line-delimited ASCII commands:

| Command | Description |
|---|---|
| `WAKE\n` | Sent when the robot begins preparing a response |
| `EMOTION:<EMOTION>\n` | Sets emotion (`HAPPY`, `ANGRY`, `SAD`, `CONFUSED`, `NEUTRAL`) |
| `EMOTION:NEUTRAL\n` | Resets robot expression back to neutral after TTS playback completes |

---

## ❓ Troubleshooting

- **Microphone not detected (`Could not find PyAudio`)**:
  Ensure PyAudio is installed:
  ```bash
  pip install pyaudio
  ```
- **"Sorry, I couldn't respond"**:
  Make sure Ollama is running (`ollama serve`) and the model is downloaded (`ollama pull mistral:7b`).
- **Serial port error**:
  Check Windows Device Manager to verify the COM port number assigned to your microcontroller and update `SERIAL_PORT` in `Keero.py`. If testing without hardware, the app automatically skips serial transmission.

