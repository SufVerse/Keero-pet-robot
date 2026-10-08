import requests
import speech_recognition as sr
import serial
import time
import asyncio
import edge_tts
import io
import pygame

# ============================== CONFIG ==============================
MODEL="mistral:7b"
SERIAL_PORT = "COM7"
BAUD_RATE = 115200

# ============================== GLOBAL UI STATE =====================
recognized_text = ""
robot_reply = ""
state = "idle"   # idle, listening, replying

# ============================== INITIALIZATION =====================
recognizer = sr.Recognizer()
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
except Exception as e:
    print(f"[WARNING] Could not open serial port {SERIAL_PORT}: {e}")
    print("[INFO] Running in hardware-free mode. Keero will speak and think without physical robot output.")
    ser = None

pygame.mixer.init()

tts_queue = asyncio.Queue()
listen_queue = asyncio.Queue()
playback_started_event = asyncio.Event()

# ============================== TTS WORKER ==========================
async def tts_worker():
    global state
    while True:
        text = await tts_queue.get()

        state = "replying"

        communicate = edge_tts.Communicate(
            text,
            voice="en-US-GuyNeural",
            rate="-10%",
            pitch="+100Hz"
        )

        audio_buffer = io.BytesIO()

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_buffer.seek(0)

        playback_started_event.clear()

        pygame.mixer.music.load(audio_buffer, "mp3")
        pygame.mixer.music.play()

        playback_started_event.set()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)

        playback_started_event.clear()
        state = "idle"

        tts_queue.task_done()

        # after playback finishes
        try:
            ser.write(b"EMOTION:NEUTRAL\n")
        except:
            pass


def detect_emotion_llm(text):
    emotion_prompt = f"""
Classify emotion as one word:
HAPPY, ANGRY, SAD, CONFUSED, NEUTRAL

Text:
{text}

Answer:
"""
    emotion = ask_llm(emotion_prompt).strip().upper()

    return emotion if emotion in ["HAPPY","ANGRY","SAD","CONFUSED","NEUTRAL"] else "NEUTRAL"

# ============================== LISTEN ==============================
async def listen_worker():
    global recognized_text, state

    while True:
        state = "listening"
        print("Listening...")

        def blocking_listen():
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=2)
                audio = recognizer.listen(source, phrase_time_limit=5)
                return recognizer.recognize_google(audio)

        try:
            text = await asyncio.to_thread(blocking_listen)
            recognized_text = text
            print("USER:", text)
            await listen_queue.put(text)

        except:
            continue

# ============================== LLM ==============================
def ask_llm(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=60
        )

        print("LLM STATUS:", response.status_code)

        data = response.json()
        print("LLM RAW:", data)

        return data.get("response", "").strip()

    except Exception as e:
        print("LLM ERROR:", e)
        return "Sorry, I couldn't respond."

# ============================== PROCESS ============================
async def process_queries():
    global recognized_text, robot_reply

    while True:
        user_text = await listen_queue.get()

        if not user_text:
            continue

        prompt = f"""
You are Keero, a cute emotional robotic pet.
Respond in 1 short sentence.

User:
{user_text}
"""

        reply = await asyncio.to_thread(ask_llm, prompt)

        robot_reply = reply
        print("KEERO:", reply)

        # 🔥 WAKE robot before replying
        try:
            ser.write(b"WAKE\n")
            await asyncio.sleep(0.2)
        except:
            pass

        # 🔥 SEND EMOTION BEFORE SPEAKING
        try:
            emotion = await asyncio.to_thread(detect_emotion_llm, user_text)
            print("Emotion:", emotion)

            try:
                ser.write(b"WAKE\n")
                await asyncio.sleep(0.2)
                ser.write(f"EMOTION:{emotion}\n".encode())
            except:
                pass   # or use your emotion detector
        except:
            pass

        await tts_queue.put(reply)

# ============================== MAIN ==============================
async def main():
    await asyncio.gather(
        tts_worker(),
        listen_worker(),
        process_queries()
    )