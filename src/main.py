"""
Main FastAPI application for AI Calling Agent.
Provides REST API endpoints and WebSocket connections for voice interaction.
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio

from src.config import get_settings
from src.agent.gemini_client import get_gemini_client
from src.agent.pipeline import VoicePipeline

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI Calling Agent",
    description="Real-time AI voice agent powered by Google Gemini",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Twilio telephony routes
from src.telephony.twilio_webhook import router as twilio_router
app.include_router(twilio_router)


# Request/Response models
class ChatMessage(BaseModel):
    """Single chat message."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str
    history: list[ChatMessage] | None = None
    system_instruction: str | None = None


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    reply: str
    model: str


# Initialize Gemini client
gemini_client = get_gemini_client()


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint to verify the service is running.
    
    Returns:
        JSONResponse: Service status
    """
    return JSONResponse(
        content={
            "status": "ok",
            "service": "ai-calling-agent",
            "version": "0.1.0"
        },
        status_code=200
    )


@app.get("/")
async def root() -> JSONResponse:
    """
    Root endpoint providing API information.
    
    Returns:
        JSONResponse: API information
    """
    return JSONResponse(
        content={
            "message": "AI Calling Agent API",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "redoc": "/redoc"
            }
        }
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat with Gemini AI using text generation.
    
    Args:
        request: ChatRequest containing message, optional history and system instruction
        
    Returns:
        ChatResponse: The AI's reply and model used
    """
    try:
        # Convert history to simple dict format if provided
        history = None
        if request.history:
            history = [
                {"role": msg.role, "content": msg.content} 
                for msg in request.history
            ]
        
        # Generate response
        reply = await gemini_client.generate_text(
            message=request.message,
            history=history,
            system_instruction=request.system_instruction
        )
        
        return ChatResponse(
            reply=reply,
            model=gemini_client.text_model
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )


@app.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice streaming.
    
    Protocol:
        - Client sends: Raw PCM audio bytes (16kHz, 16-bit, mono)
        - Server sends: Raw PCM audio bytes (24kHz, 16-bit, mono)
    """
    await websocket.accept()
    print("🔌 WebSocket client connected")
    
    pipeline = None
    
    try:
        # Create voice pipeline
        pipeline = VoicePipeline(
            system_instruction="You are a helpful AI voice assistant. Be conversational and concise.",
            sample_rate=16000
        )
        
        # Audio input queue for the generator
        audio_queue: asyncio.Queue = asyncio.Queue()
        
        # Async generator to feed audio input
        async def audio_input_generator():
            while True:
                audio_chunk = await audio_queue.get()
                if audio_chunk is None:  # Sentinel to stop
                    break
                yield audio_chunk
        
        # Task to receive audio from client
        async def receive_audio():
            try:
                while True:
                    data = await websocket.receive_bytes()
                    await audio_queue.put(data)
            except WebSocketDisconnect:
                await audio_queue.put(None)  # Signal end
            except Exception as e:
                print(f"Error receiving audio: {e}")
                await audio_queue.put(None)
        
        # Start receive task
        receive_task = asyncio.create_task(receive_audio())
        
        # Process and send audio back to client
        try:
            async for output_audio in pipeline.process_audio_stream(audio_input_generator()):
                await websocket.send_bytes(output_audio)
        except Exception as e:
            print(f"Error in audio pipeline: {e}")
        finally:
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
        
    except WebSocketDisconnect:
        print("👋 WebSocket client disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
    finally:
        if pipeline:
            pipeline.stop()
        print("🔌 WebSocket connection closed")


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
