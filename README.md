# AI Voice Assistant

A lightweight AI-powered voice assistant that enables natural voice conversations in Arabic. The assistant listens to the user's speech, converts it into text, understands the request using a Large Language Model (LLM), performs live web searches when necessary, and responds with natural-sounding Arabic speech.

Unlike many local AI assistants, this project relies entirely on cloud services, making it fast, lightweight, and capable of running on almost any computer without requiring a dedicated GPU.

---

# Features

-  Speech-to-Text using Google Speech Recognition
-  AI-powered conversations using Llama 3.3 (Groq)
-  Automatic live web search using DuckDuckGo
-  Natural Egyptian Arabic voice using Microsoft Edge TTS (Salma Neural)
-  Short-term conversation memory for contextual conversations
-  Fast cloud inference with low latency
-  No GPU required

---

# System Architecture

```
                User Speech
                     │
                     ▼
        Google Speech Recognition
                     │
                     ▼
              User Text
                     │
                     ▼
           Llama 3.3 (Groq API)
                     │
        ┌────────────┴────────────┐
        │                         │
        │ Need web search?        │
        │                         │
        ▼                         ▼
 DuckDuckGo Search          Generate Response
        │                         │
        └────────────┬────────────┘
                     ▼
        Microsoft Edge TTS (Salma)
                     │
                     ▼
               Spoken Response
```

---

# Core AI Components

## 1. Speech-to-Text (STT)

The assistant captures the user's speech using a microphone and converts it into text.

### Technology

- SpeechRecognition
- Google Speech Recognition API

### Features

- Supports Arabic (Egyptian dialect - ar-EG)
- Automatic speech endpoint detection
- Ambient noise calibration
- Continuous microphone listening

---

## 2. Large Language Model (LLM)

The reasoning engine of the assistant.

### Technology

- Llama 3.3 70B Versatile
- Groq API

### Features

- Understands Arabic requests
- Responds in Modern Standard Arabic
- Maintains short conversation memory
- Uses Function Calling
- Automatically decides when web search is required

---

## 3. Web Search Tool

The assistant includes an integrated search tool that can be called automatically by the language model.

### Technology

- DuckDuckGo Search (DDGS)

### Features

- Current news
- Sports results
- Recent events
- Up-to-date information

The LLM decides automatically whether the search tool should be used.

---

## 4. Text-to-Speech (TTS)

Converts the generated response into natural speech.

### Technology

- Microsoft Edge TTS

### Voice

- ar-EG-SalmaNeural

### Features

- Natural Egyptian Arabic voice
- Reduced speaking rate (-10%)
- Audio playback using Pygame

---

# Conversation Memory

The assistant stores the latest conversation history, allowing it to remember previous user messages during the session and generate context-aware responses.

To prevent excessive token usage, only the most recent conversation turns are retained.

---

# Technologies Used

- Python
- Groq API
- Llama 3.3 70B Versatile
- SpeechRecognition
- Google Speech Recognition
- Edge TTS
- DuckDuckGo Search
- Pygame
- Python Dotenv

---

# Installation

## Clone the repository

```bash
git clone https://github.com/yourusername/AI_Voice_Agent.git

cd AI_Voice_Agent
```

---

## Install dependencies

Create a `requirements.txt` file containing:

```txt
SpeechRecognition
PyAudio
groq
edge-tts
pygame
python-dotenv
ddgs
```

Then install:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a file named `.env` in the project root.

```env
GROQ_API_KEY=your_groq_api_key
```

Replace the value with your own Groq API key.

---

# Running the Project

```bash
python agent.py
```

After initialization, the assistant will display:

```
[OK] System Ready
```

Start speaking through your microphone.

Say:

- سلام
- وداعاً

to exit the application.

---

# Project Structure

```
AI_Voice_Agent/
│
├── agent.py
├── README.md
├── .env
├── .gitignore
└── requirements.txt
```

---

# Requirements

- Python 3.10+
- Internet connection
- Microphone
- Groq API Key

---

# Future Improvements

- Voice activity detection (VAD)
- Wake word detection
- Streaming speech generation
- Support for multiple languages
- Long-term memory
- GUI version
- Local LLM support

---

# License

This project is intended for educational and research purposes.
