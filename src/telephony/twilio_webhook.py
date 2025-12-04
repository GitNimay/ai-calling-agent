"""
Twilio Media Streams integration for phone call support.
Handles incoming calls and bidirectional audio streaming.
"""
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
import asyncio
import json
import base64
import audioop

from src.config import get_settings
from src.agent.pipeline import VoicePipeline

settings = get_settings()
router = APIRouter(prefix="/twilio", tags=["telephony"])


@router.post("/incoming")
async def handle_incoming_call(request: Request):
    """
    Handle incoming Twilio voice call.
    Returns TwiML to connect the call to our media stream WebSocket.
    
    Returns:
        Response: TwiML XML response
    """
    # Get the server's WebSocket URL
    # In production, this should be your public WSS URL
    host = request.headers.get("host", "localhost:8000")
    protocol = "wss" if "https" in str(request.url) else "ws"
    ws_url = f"{protocol}://{host}/twilio/media"
    
    # TwiML response to connect to media stream
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Hello! You are now connected to an AI voice assistant powered by Gemini.</Say>
    <Connect>
        <Stream url="{ws_url}" />
    </Connect>
</Response>"""
    
    return Response(content=twiml, media_type="application/xml")


@router.websocket("/media")
async def handle_media_stream(websocket: WebSocket):
    """
    Handle Twilio Media Stream WebSocket connection.
    
    Twilio sends:
        - JSON messages with base64-encoded mulaw audio
    
    We send back:
        - JSON messages with base64-encoded mulaw audio
    """
    await websocket.accept()
    print("📞 Twilio call connected")
    
    pipeline = None
    stream_sid = None
    
    try:
        # Audio queues
        audio_input_queue: asyncio.Queue = asyncio.Queue()
        
        # Async generator for audio input
        async def audio_input_generator():
            while True:
                audio_chunk = await audio_input_queue.get()
                if audio_chunk is None:
                    break
                yield audio_chunk
        
        # Create voice pipeline
        pipeline = VoicePipeline(
            system_instruction="You are a helpful AI phone assistant. Be conversational, concise, and friendly.",
            sample_rate=8000  # Twilio uses 8kHz
        )
        
        # Task to receive Twilio messages
        async def receive_twilio_messages():
            nonlocal stream_sid
            try:
                while True:
                    message = await websocket.receive_json()
                    event = message.get("event")
                    
                    if event == "start":
                        stream_sid = message.get("streamSid")
                        print(f"📞 Stream started: {stream_sid}")
                    
                    elif event == "media":
                        # Decode mulaw audio from Twilio
                        payload = message.get("media", {}).get("payload", "")
                        if payload:
                            # Decode base64
                            mulaw_audio = base64.b64decode(payload)
                            
                            # Convert mulaw to linear PCM (16-bit)
                            pcm_audio = audioop.ulaw2lin(mulaw_audio, 2)
                            
                            # Put in queue for pipeline
                            await audio_input_queue.put(pcm_audio)
                    
                    elif event == "stop":
                        print("📞 Stream stopped")
                        await audio_input_queue.put(None)
                        break
                        
            except WebSocketDisconnect:
                await audio_input_queue.put(None)
            except Exception as e:
                print(f"Error receiving Twilio messages: {e}")
                await audio_input_queue.put(None)
        
        # Start receive task
        receive_task = asyncio.create_task(receive_twilio_messages())
        
        # Process audio and send back to Twilio
        try:
            async for output_audio in pipeline.process_audio_stream(audio_input_generator()):
                if stream_sid:
                    # Convert PCM to mulaw for Twilio
                    # Note: Gemini outputs 24kHz, need to resample to 8kHz for Twilio
                    # For now, simple decimation (in production, use proper resampling)
                    mulaw_audio = audioop.lin2ulaw(output_audio, 2)
                    
                    # Encode to base64
                    payload = base64.b64encode(mulaw_audio).decode('utf-8')
                    
                    # Send Twilio media message
                    media_message = {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {
                            "payload": payload
                        }
                    }
                    await websocket.send_json(media_message)
        except Exception as e:
            print(f"Error in Twilio audio pipeline: {e}")
        finally:
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
    
    except WebSocketDisconnect:
        print("📞 Twilio call disconnected")
    except Exception as e:
        print(f"❌ Twilio WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
    finally:
        if pipeline:
            pipeline.stop()
        print("📞 Twilio call ended")
