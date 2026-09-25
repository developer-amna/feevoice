import asyncio
import json
import os
import queue

import sounddevice as sd
import websockets
from dotenv import load_dotenv
from groq import Groq
import pyttsx3

from flask import Flask, render_template, jsonify
import threading

app = Flask(__name__)
app_state = {"transcript": "", "agent_reply": "", "fee_card": None, "state": "listening"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/status")
def status():
    return jsonify(app_state)


def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)

load_dotenv()

with open("students.json", "r", encoding="utf-8") as f:
    students_db = json.load(f)


def get_fee_status(student_name: str, roll_number: str = None):
    student_name = student_name.strip().lower()
    student = students_db.get(student_name)
    if not student:
        return {"error": f"No record found for {student_name}"}

    if roll_number is None:
        return {"error": "Roll number required to verify identity before sharing fee details."}

        def normalize(s):
            return s.strip().lower().replace("-", "").replace(" ", "")

        if normalize(student["roll_number"]) != normalize(roll_number):
            return {"error": "Roll number does not match our records. Cannot share fee details."}

    app_state["fee_card"] = student
    return student


tools = [
        {
        "type": "function",
        "function": {
            "name": "get_fee_status",
            "description": "Get a student's fee status (total fee, amount paid, amount due, due date) by their full name and roll number. Roll number is required to verify identity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "The student's full name, e.g. 'Ali Khan'",
                    },
                    "roll_number": {
                        "type": "string",
                        "description": "The student's roll number, e.g. 'BSCS-021'. Required to verify identity.",
                    },
                },
                "required": ["student_name", "roll_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_payment_link",
            "description": "Generate a payment link for a student to pay their remaining due fee amount.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "The student's full name, e.g. 'Ali Khan'",
                    }
                },
                "required": ["student_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a reminder for a student to be notified before their fee due date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "The student's full name, e.g. 'Ali Khan'",
                    },
                    "days_before": {
                        "type": "integer",
                        "description": "How many days before the due date to remind them. Default 3.",
                    },
                },
                "required": ["student_name"],
            },
        },
    },
]
conversation_history = []
def generate_payment_link(student_name: str):
    student_name = student_name.strip().lower()
    student = students_db.get(student_name)
    if not student:
        return {"error": f"No record found for {student_name}"}
    if student["due"] == 0:
        return {"message": "No dues pending, nothing to pay."}
    return {
        "payment_link": f"https://easyfee.example.com/pay?student={student_name.replace(' ', '-')}&amount={student['due']}",
        "amount": student["due"],
        "methods": ["JazzCash", "EasyPaisa", "Bank Transfer"],
    }
    
def set_reminder(student_name: str, days_before: int = 3):
    student_name = student_name.strip().lower()
    student = students_db.get(student_name)
    if not student:
        return {"error": f"No record found for {student_name}"}
    if not student.get("due_date"):
        return {"message": "No due date on record, nothing to remind about."}

    with open("reminders.json", "r", encoding="utf-8") as f:
        reminders = json.load(f)

    reminders.append(
        {
            "student_name": student_name,
            "due_date": student["due_date"],
            "remind_days_before": days_before,
        }
    )

    with open("reminders.json", "w", encoding="utf-8") as f:
        json.dump(reminders, f, indent=2)

    return {
        "message": f"Reminder set for {days_before} days before the due date ({student['due_date']})."
    }

ASSEMBLYAI_API_KEY = os.environ["ASSEMBLYAI_API_KEY"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

groq_client = Groq(api_key=GROQ_API_KEY)


SAMPLE_RATE = 16000
CHANNELS = 1

audio_queue = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    audio_queue.put(bytes(indata))


def speak(text):
    print(f"Agent: {text}")
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def ask_groq(user_text):
    conversation_history.append({"role": "user", "content": user_text})

    messages = [
        {
            "role": "system",
            "content": (
                "You are FeeVoice, a friendly voice assistant that helps students with "
                "college fee questions. Always reply in simple English only, no matter "
                "what language the student speaks in. Keep replies short, 1-2 sentences, "
                "natural and conversational. When a student asks about their fee, ask for "
                "their full name if you don't have it yet, then use the get_fee_status tool. "
                "When a student wants to pay or asks for a payment link, ALWAYS use the "
                "Before sharing any fee details, always ask for both the student's full name AND their roll number to verify identity. "
                "generate_payment_link tool to get the real link — never make up or guess "
                "a payment link yourself. Remember the student's name once they tell you, "
                "so you don't need to ask again."
            ),
        }
    ] + conversation_history

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools,
    )

    message = response.choices[0].message

    if message.tool_calls:
        messages.append(message)
        conversation_history.append(message)
        for tool_call in message.tool_calls:
            
            args = json.loads(tool_call.function.arguments)
            if tool_call.function.name == "get_fee_status":
                result = get_fee_status(
                    args["student_name"], args.get("roll_number")
                )
            elif tool_call.function.name == "generate_payment_link":
                result = generate_payment_link(args["student_name"])
            elif tool_call.function.name == "set_reminder":
                    result = set_reminder(
                        args["student_name"], args.get("days_before", 3)
                    )
            else:
                result = {"error": "Unknown tool"}
            tool_msg = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            }
            messages.append(tool_msg)
            conversation_history.append(tool_msg)
        followup = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
        )
        reply = followup.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        return reply

    conversation_history.append({"role": "assistant", "content": message.content})
    return message.content

async def send_audio(ws):
    loop = asyncio.get_event_loop()
    while True:
        data = await loop.run_in_executor(None, audio_queue.get)
        await ws.send(data)


async def receive_transcripts(ws):
    async for message in ws:
        data = json.loads(message)
        if data.get("type") == "Turn":
            transcript = data.get("transcript", "")
            end_of_turn = data.get("end_of_turn", False)
            if transcript:
                print(f"You: {transcript}", end="\r")
                app_state["transcript"] = transcript
            if end_of_turn and transcript.strip():
                print(f"You: {transcript}")
                app_state["state"] = "thinking"
                reply = ask_groq(transcript)
                app_state["agent_reply"] = reply
                app_state["state"] = "speaking"
                speak(reply)
                app_state["state"] = "listening"


async def main():
    url = "wss://streaming.assemblyai.com/v3/ws?sample_rate=16000&format_turns=true"
    headers = {"Authorization": ASSEMBLYAI_API_KEY}
    async with websockets.connect(url, additional_headers=headers) as ws:
        print("Connected. Start speaking (Ctrl+C to stop)...")
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=audio_callback,
            blocksize=800,
        ):
            await asyncio.gather(send_audio(ws), receive_transcripts(ws))


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")