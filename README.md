MIT License

Copyright (c) 2026 FeeVoice

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Save kar lo (Ctrl+S).

Ho jaye to "ho gaya" bol dena — phir Step 4 mein hum README.md likhenge (yeh sabse zaroori hai, judges yehi pehle padhte hain).

ho gya

Step 4: README.md Likho

Yeh sabse zaroori file hai — judges pehle yehi padhte hain samajhne ke liye ke project kya hai.

feevoice folder ke andar ek nayi file banao naam README.md.

Ismein yeh poora content paste karo:

markdown
# 🎓 FeeVoice — Voice-Based Student Fee Assistant

FeeVoice is a real-time voice AI agent that helps students check their college fee status, generate payment links, and set due-date reminders — all through natural conversation, no login or app navigation required.

Built for the AssemblyAI Voice Agent Hackathon (lablab.ai).

## 💡 The Problem

Students in Pakistan often have to visit the bank or navigate confusing portals just to check their fee status or due dates. FeeVoice makes this as simple as asking a question out loud.

## ✨ Features

- **Real-time voice conversation** — powered by AssemblyAI's Realtime Speech-to-Text API
- **Identity verification** — requires both name and roll number before sharing any fee data (privacy-first design)
- **Fee status lookup** — total fee, amount paid, amount due, due date
- **Payment link generation** — mock JazzCash/EasyPaisa/bank transfer integration
- **Due-date reminders** — students can ask to be reminded before their fee is due
- **Conversation memory** — the agent remembers context across the conversation
- **Live visual dashboard** — transcript, agent reply, fee card, and a listening/thinking/speaking state indicator, all updating in real time in the browser

## 🛠️ Tech Stack

- **Speech-to-Text**: AssemblyAI Realtime Streaming API
- **LLM + Tool Calling**: Groq (openai/gpt-oss-120b)
- **Text-to-Speech**: pyttsx3 (offline)
- **Backend**: Python, asyncio, websockets, Flask
- **Frontend**: HTML/CSS/JavaScript (polled live dashboard)

## 🚀 How to Run Locally

1. Clone this repository and navigate into it:

git clone <your-repo-url>
cd feevoice


2. Create a virtual environment and activate it:

python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux


3. Install dependencies:

pip install -r requirements.txt


4. Create a `.env` file in the project root with your API keys:

ASSEMBLYAI_API_KEY=your_assemblyai_key
GROQ_API_KEY=your_groq_key


5. Run the agent:

python main.py


6. Open your browser to `http://localhost:5000`, click **"Start Listening"**, allow microphone access, and start speaking!

## 🌐 Live Demo

Try it live: **[Live App Link](https://conclude-manly-alfalfa.ngrok-free.dev)**

This app runs directly in the browser — the microphone is captured via the Web Audio API and speech output uses the browser's built-in speech synthesis, so it works both locally and when deployed online.

**Note**: This demo link is active while the developer's local server is running. Please contact for a live demonstration if the link is inactive.