"""
Gemini API client wrapper for text generation and Live API audio streaming.
Provides simplified interfaces for interacting with Google Gemini models.
"""
import os
import io
import wave
from typing import Optional, AsyncGenerator
from google import genai
from google.genai import types

from src.config import get_settings

settings = get_settings()


class GeminiClient:
    """Wrapper for Google Gemini API client."""
    
    def __init__(self):
        """Initialize the Gemini client with API key from settings."""
        self.api_key = settings.GEMINI_API_KEY
        self.text_model = settings.GEMINI_MODEL_TEXT
        self.live_model = settings.GEMINI_MODEL_LIVE
        
        # Initialize the client
        self.client = genai.Client(api_key=self.api_key)
    
    async def generate_text(
        self, 
        message: str, 
        history: Optional[list[dict]] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate text response from Gemini using the text model.
        
        Args:
            message: The user's message/prompt
            history: Optional conversation history as list of dicts with 'role' and 'content'
            system_instruction: Optional system instruction for the model
            
        Returns:
            str: The model's text response
        """
        try:
            # Build the conversation context
            contents = []
            
            # Add history if provided
            if history:
                for msg in history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part(text=content)]
                    ))
            
            # Add current message
            contents.append(types.Content(
                role="user",
                parts=[types.Part(text=message)]
            ))
            
            # Generate response
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
            
            response = await self.client.aio.models.generate_content(
                model=self.text_model,
                contents=contents,
                config=config
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
    
    async def stream_text(
        self, 
        message: str, 
        history: Optional[list[dict]] = None,
        system_instruction: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream text response from Gemini token by token.
        
        Args:
            message: The user's message/prompt
            history: Optional conversation history
            system_instruction: Optional system instruction
            
        Yields:
            str: Text chunks as they arrive
        """
        try:
            # Build the conversation context
            contents = []
            
            # Add history if provided
            if history:
                for msg in history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part(text=content)]
                    ))
            
            # Add current message
            contents.append(types.Content(
                role="user",
                parts=[types.Part(text=message)]
            ))
            
            # Generate streaming response
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
            
            stream = await self.client.aio.models.generate_content_stream(
                model=self.text_model,
                contents=contents,
                config=config
            )
            
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            raise Exception(f"Error streaming text: {str(e)}")
    
    async def stream_audio_to_gemini(
        self,
        audio_pcm: bytes,
        system_instruction: Optional[str] = None,
        sample_rate: int = 16000
    ) -> bytes:
        """
        Send audio to Gemini Live API and get audio response.
        
        Args:
            audio_pcm: Raw PCM audio bytes (16-bit mono)
            system_instruction: Optional system instruction
            sample_rate: Sample rate of input audio (default: 16000Hz)
            
        Returns:
            bytes: Raw PCM audio response (24kHz, 16-bit mono)
        """
        try:
            # Configure Live API session
            config = {
                "response_modalities": ["AUDIO"],
            }
            if system_instruction:
                config["system_instruction"] = system_instruction
            
            # Connect to Live API
            async with self.client.aio.live.connect(
                model=self.live_model, 
                config=config
            ) as session:
                # Send audio input
                await session.send(
                    input=types.LiveClientRealtimeInput(
                        media_chunks=[
                            types.Blob(
                                data=audio_pcm,
                                mime_type=f"audio/pcm;rate={sample_rate}"
                            )
                        ]
                    )
                )
                
                # Collect audio response
                audio_response = bytearray()
                async for response in session.receive():
                    # Check for audio data in the response
                    if response.data is not None:
                        audio_response.extend(response.data)
                
                return bytes(audio_response)
                
        except Exception as e:
            raise Exception(f"Error in Live API audio streaming: {str(e)}")
    
    async def stream_audio_bidirectional(
        self,
        audio_generator: AsyncGenerator[bytes, None],
        system_instruction: Optional[str] = None,
        sample_rate: int = 16000
    ) -> AsyncGenerator[bytes, None]:
        """
        Bidirectional audio streaming with Gemini Live API.
        Accepts an async generator of audio chunks and yields audio responses.
        
        Args:
            audio_generator: Async generator yielding PCM audio chunks
            system_instruction: Optional system instruction
            sample_rate: Sample rate of input audio (default: 16000Hz)
            
        Yields:
            bytes: PCM audio response chunks (24kHz, 16-bit mono)
        """
        try:
            # Configure Live API session
            config = {
                "response_modalities": ["AUDIO"],
            }
            if system_instruction:
                config["system_instruction"] = system_instruction
            
            async with self.client.aio.live.connect(
                model=self.live_model,
                config=config
            ) as session:
                # Start a task to send audio chunks
                async def send_audio():
                    try:
                        async for audio_chunk in audio_generator:
                            if audio_chunk:
                                await session.send(
                                    input=types.LiveClientRealtimeInput(
                                        media_chunks=[
                                            types.Blob(
                                                data=audio_chunk,
                                                mime_type=f"audio/pcm;rate={sample_rate}"
                                            )
                                        ]
                                    )
                                )
                    except Exception as e:
                        print(f"Error sending audio: {e}")
                
                # Create send task
                import asyncio
                send_task = asyncio.create_task(send_audio())
                
                # Receive and yield audio responses
                try:
                    async for response in session.receive():
                        if response.data is not None:
                            yield response.data
                finally:
                    # Ensure send task is cleaned up
                    send_task.cancel()
                    try:
                        await send_task
                    except asyncio.CancelledError:
                        pass
                        
        except Exception as e:
            raise Exception(f"Error in bidirectional audio streaming: {str(e)}")
    
    async def process_audio_opensource(
        self,
        audio_pcm: bytes,
        sample_rate: int = 16000,
        system_instruction: Optional[str] = None
    ) -> bytes:
        """
        Process audio using open-source pipeline: Whisper STT → Gemini Text → Coqui TTS.
        This is a fully open-source alternative to Gemini Live API.
        
        Args:
            audio_pcm: Raw PCM audio bytes (16-bit mono)
            sample_rate: Sample rate of input audio
            system_instruction: Optional system instruction
            
        Returns:
            bytes: PCM audio response (22050Hz, 16-bit mono from Coqui TTS)
        """
        try:
            # Import open-source engines
            from src.stt.whisper_engine import get_whisper_stt
            from src.tts.coqui_engine import get_coqui_tts
            
            print("🎙️ Step 1/3: Transcribing audio with Whisper...")
            # Step 1: Speech-to-Text with Whisper
            stt = get_whisper_stt(model_size="base")
            transcribed_text = stt.transcribe_audio_bytes(
                audio_bytes=audio_pcm,
                sample_rate=sample_rate
            )
            print(f"   → Transcribed: {transcribed_text}")
            
            print("🤖 Step 2/3: Generating response with Gemini...")
            # Step 2: Text generation with Gemini
            response_text = await self.generate_text(
                message=transcribed_text,
                system_instruction=system_instruction or "You are a helpful voice assistant. Be concise and natural."
            )
            print(f"   → Response: {response_text[:100]}...")
            
            print("🔊 Step 3/3: Synthesizing speech with Coqui TTS...")
            # Step 3: Text-to-Speech with Coqui TTS
            tts = get_coqui_tts()
            audio_response = tts.synthesize_to_bytes(text=response_text)
            print(f"   → Synthesized {len(audio_response)} bytes")
            
            return audio_response
            
        except Exception as e:
            raise Exception(f"Error in open-source voice pipeline: {str(e)}")


# Global client instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Get or create the global Gemini client instance.
    
    Returns:
        GeminiClient: Singleton client instance
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
