# 🤖 AI Calling Agent

A **100% free, open-source AI calling/voice agent** powered by **Google Gemini** for real-time voice interactions.

## 🎯 Features

- **Real-time voice conversations** using Gemini Live API
- **Text chat** with Gemini for text-based interactions
- **FastAPI backend** with WebSocket support for duplex audio streaming
- **Free & open-source** components (no proprietary paid APIs)
- **Modular architecture** for easy extension
- **Optional Twilio integration** for phone call support

## 🧱 Tech Stack

- **Language:** Python 3.11+
- **Web Framework:** FastAPI
- **Real-time:** WebSocket
- **LLM:** Google Gemini API (text generation)
- **Voice (Option 1):** Gemini Live API (native audio-to-audio)
- **Voice (Option 2 - Open Source):** 
  - **STT:** faster-whisper (OpenAI Whisper)
  - **TTS:** Coqui TTS
- **Telephony (optional):** Twilio Media Streams

## 📁 Project Structure

```
ai-calling-agent/
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── src/
    ├── __init__.py
    ├── config.py           # Environment & settings
    ├── main.py             # FastAPI app (health, /chat, /ws/voice)
    ├── agent/
    │   ├── __init__.py
    │   ├── gemini_client.py  # Gemini text + Live API wrapper
    │   └── pipeline.py       # Duplex audio pipeline
    ├── stt/
    │   ├── __init__.py
    │   └── whisper_engine.py # Local STT engine
    ├── tts/
    │   ├── __init__.py
    │   └── coqui_engine.py   # Local TTS engine
    ├── telephony/
    │   ├── __init__.py
    │   └── twilio_webhook.py # Twilio handler
    └── demos/
        ├── local_text_demo.py
        └── local_voice_demo.py
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd "d:\nimesh-portfolio\ai calling agent"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
# source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your Gemini API key
# Get your key from: https://aistudio.google.com/app/apikey
```

Update `.env` with your actual credentials:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 4. Run the Server

```bash
# Option 1: Using uvicorn directly
uvicorn src.main:app --reload

# Option 2: Using Python
python -m src.main
```

The server will start at: `http://localhost:8000`

### 5. Test the Health Endpoint

```bash
# Using curl
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","service":"ai-calling-agent","version":"0.1.0"}
```

You can also visit:
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📝 Development Status

### ✅ Phase 1 - Bootstrap (COMPLETED)
- [x] Project structure
- [x] FastAPI app with `/health` endpoint
- [x] Configuration management
- [x] Environment setup

### ✅ Phase 2 - Text Chat (COMPLETED)
- [x] Gemini text client wrapper
- [x] POST `/chat` endpoint
- [x] Local text demo script

### ✅ Phase 3 - Local Voice Demo (COMPLETED)
- [x] Gemini Live API integration
- [x] Audio file processing demo

### ✅ Phase 4 - WebSocket Voice (COMPLETED)
- [x] Real-time audio pipeline
- [x] WebSocket `/ws/voice` endpoint

### ✅ Phase 5 - Twilio Integration (COMPLETED)
- [x] Twilio webhook handler
- [x] Phone call support

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key | **Required** |
| `GEMINI_MODEL_TEXT` | Model for text generation | `gemini-2.0-flash-exp` |
| `GEMINI_MODEL_LIVE` | Model for live audio | `gemini-2.0-flash-exp` |
| `PORT` | Server port | `8000` |
| `HOST` | Server host | `0.0.0.0` |
| `AUDIO_SAMPLE_RATE` | Audio sample rate (Hz) | `16000` |

## 📚 API Endpoints

### GET `/health`
Health check endpoint
```bash
curl http://localhost:8000/health
```

### GET `/`
API information
```bash
curl http://localhost:8000/
```

### POST `/chat`
Text chat with Gemini AI
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### WebSocket `/ws/voice`
Real-time voice streaming
- **Client sends:** Raw PCM audio (16kHz, 16-bit, mono)
- **Server sends:** Raw PCM audio (24kHz, 16-bit, mono)

### POST `/twilio/incoming`
Twilio webhook for incoming calls (returns TwiML)

### WebSocket `/twilio/media`
Twilio Media Streams endpoint for phone calls

## 🎙️ Usage Examples

### Text Chat Demo
```bash
python -m src.demos.local_text_demo
```

### Local Voice Demo
```bash
# Creates test audio if needed
python -m src.demos.local_voice_demo
```

### Open-Source Voice Demo (Whisper + Coqui TTS)
```bash
# Uses 100% open-source: Whisper STT → Gemini → Coqui TTS
python -m src.demos.opensource_voice_demo
```

### WebSocket Voice Client
Connect to `ws://localhost:8000/ws/voice` and send/receive PCM audio

### Twilio Phone Calls
1. Configure Twilio phone number webhook: `https://your-domain.com/twilio/incoming`
2. Call the number to talk to the AI agent

## 🤝 Contributing

This is an open-source project. Contributions are welcome!

## 📄 License

MIT License - Free to use for any purpose.

## 🔗 Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pipecat Framework](https://github.com/pipecat-ai/pipecat)
- [Twilio Media Streams](https://www.twilio.com/docs/voice/media-streams)

---

**Built with ❤️ using free & open-source technologies**
