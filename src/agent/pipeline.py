"""
Real-time voice pipeline for bidirectional audio streaming with Gemini Live API.
Manages WebSocket connections and audio flow.
"""
import asyncio
from typing import AsyncGenerator, Optional
from src.agent.gemini_client import get_gemini_client


class VoicePipeline:
    """
    Manages bidirectional audio streaming between client and Gemini Live API.
    """
    
    def __init__(
        self,
        system_instruction: Optional[str] = None,
        sample_rate: int = 16000
    ):
        """
        Initialize the voice pipeline.
        
        Args:
            system_instruction: Optional system instruction for Gemini
            sample_rate: Audio sample rate (default: 16000Hz)
        """
        self.system_instruction = system_instruction or "You are a helpful AI assistant for voice calls. Be concise and natural."
        self.sample_rate = sample_rate
        self.client = get_gemini_client()
        self._active = False
    
    async def process_audio_stream(
        self,
        audio_input_generator: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[bytes, None]:
        """
        Process bidirectional audio stream.
        
        Args:
            audio_input_generator: Async generator yielding input PCM audio chunks
            
        Yields:
            bytes: Output PCM audio chunks from Gemini (24kHz)
        """
        self._active = True
        
        try:
            # Stream audio bidirectionally through Gemini
            async for audio_chunk in self.client.stream_audio_bidirectional(
                audio_generator=audio_input_generator,
                system_instruction=self.system_instruction,
                sample_rate=self.sample_rate
            ):
                if not self._active:
                    break
                yield audio_chunk
                
        except Exception as e:
            print(f"Error in voice pipeline: {e}")
            raise
        finally:
            self._active = False
    
    def stop(self):
        """Stop the pipeline."""
        self._active = False
    
    @property
    def is_active(self) -> bool:
        """Check if pipeline is active."""
        return self._active
