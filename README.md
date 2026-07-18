# Core AI Components

The project consists of three main AI systems that work together to provide a complete voice assistant experience.

## 1. Speech-to-Text (STT)

The Speech-to-Text module serves as the assistant's listening component. It captures the user's speech through the microphone and converts it into text using the **SpeechRecognition** library with **Google Speech Recognition**.

The system is configured to support **Arabic (Egyptian dialect - ar-EG)** and includes optimized settings for ambient noise calibration, speech pause detection, and timeout handling to improve recognition accuracy and provide a smooth conversation flow.

---

## 2. Large Language Model (LLM)

The Large Language Model acts as the core intelligence of the voice assistant. It receives the transcribed text, understands the user's request, and generates an appropriate response.

This project uses **Llama 3.3 70B Versatile**, hosted on the **Groq** platform, which provides high-speed inference with low latency.

### Key Features

* Generates responses exclusively in Modern Standard Arabic.
* Produces concise, clear, and direct answers.
* Avoids slang and Latin-script Arabic (Arabizi).

### Web Search Integration

The assistant is equipped with a custom tool called **`search_web`**, powered by **DuckDuckGo Search**.

Whenever the user asks about recent events or information that requires up-to-date knowledge, the LLM automatically invokes the search tool, retrieves relevant search results, and generates an informed response based on the retrieved information.

---

## 3. Text-to-Speech (TTS)

The Text-to-Speech module converts the generated text response into natural-sounding speech.

The project uses **Chatterbox Multilingual TTS**, an advanced multilingual speech synthesis model capable of generating high-quality Arabic speech with realistic pronunciation and expressive voice characteristics.

The application automatically detects the available hardware:

* If an NVIDIA GPU with CUDA support is available, inference is accelerated using the GPU.
* Otherwise, the model runs on the CPU.

The generated audio is played back using the **Pygame** audio library.

---

# System Requirements

To run the project, install the following Python packages:

| Library               | Purpose                                                          |
| --------------------- | ---------------------------------------------------------------- |
| **SpeechRecognition** | Converts speech into text.                                       |
| **PyAudio**           | Captures audio from the microphone.                              |
| **Groq**              | Provides access to the Groq API for running the Llama 3.3 model. |
| **Pygame**            | Handles audio playback.                                          |
| **Torch**             | Core deep learning framework required for AI models.             |
| **Torchaudio**        | Audio processing utilities for PyTorch.                          |
| **Chatterbox**        | Multilingual Text-to-Speech model.                               |
| **python-dotenv**     | Loads environment variables from a `.env` file.                  |
| **duckduckgo-search** | Enables real-time web search functionality.                      |

## Installation

```bash
pip install SpeechRecognition
pip install pyaudio
pip install groq
pip install pygame
pip install torch torchaudio
pip install chatterbox
pip install python-dotenv
pip install duckduckgo-search
```

> **Note:** Standard Python libraries such as `os`, `json`, and `re` are included with Python and do not require separate installation.
