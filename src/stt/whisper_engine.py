"""
Speech-to-Text engine using faster-whisper (OpenAI Whisper).
Provides transcription of audio to text.
"""
import numpy as np
from typing import Optional
from pathlib import Path

try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    print("Warning: faster-whisper not installed. STT will not work.")


class WhisperSTT:
    """
    Speech-to-Text engine using faster-whisper.
    """
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Initialize Whisper STT engine.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
            device: Device to run on (cpu, cuda)
            compute_type: Compute type (int8, float16, float32)
        """
        if not HAS_WHISPER:
            raise ImportError("faster-whisper not installed. Run: pip install faster-whisper")
        
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        
        print(f"📥 Loading Whisper model ({model_size})...")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        print(f"✅ Whisper model loaded")
    
    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es')
            
        Returns:
            str: Transcribed text
        """
        print(f"🎤 Transcribing audio: {audio_path}")
        
        # Transcribe
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5
        )
        
        # Collect all segments
        text = " ".join([segment.text for segment in segments])
        
        print(f"✅ Transcription complete: {text[:100]}...")
        return text.strip()
    
    def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        sample_rate: int = 16000,
        language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio from bytes (PCM format).
        
        Args:
            audio_bytes: Raw PCM audio bytes
            sample_rate: Sample rate of audio
            language: Optional language code
            
        Returns:
            str: Transcribed text
        """
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_float = audio_array.astype(np.float32) / 32768.0
        
        # Transcribe
        segments, info = self.model.transcribe(
            audio_float,
            language=language,
            beam_size=5
        )
        
        # Collect all segments
        text = " ".join([segment.text for segment in segments])
        
        return text.strip()


# Global instance
_whisper_stt: Optional[WhisperSTT] = None


def get_whisper_stt(model_size: str = "base") -> WhisperSTT:
    """
    Get or create global Whisper STT instance.
    
    Args:
        model_size: Whisper model size
        
    Returns:
        WhisperSTT: STT engine instance
    """
    global _whisper_stt
    if _whisper_stt is None:
        _whisper_stt = WhisperSTT(model_size=model_size)
    return _whisper_stt
