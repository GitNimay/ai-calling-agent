"""
Text-to-Speech engine using Coqui TTS.
Provides speech synthesis from text.
"""
import io
import numpy as np
from typing import Optional

try:
    from TTS.api import TTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("Warning: Coqui TTS not installed. TTS will not work.")


class CoquiTTS:
    """
    Text-to-Speech engine using Coqui TTS.
    """
    
    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        gpu: bool = False
    ):
        """
        Initialize Coqui TTS engine.
        
        Args:
            model_name: TTS model name
            gpu: Whether to use GPU
        """
        if not HAS_TTS:
            raise ImportError("Coqui TTS not installed. Run: pip install TTS")
        
        self.model_name = model_name
        self.gpu = gpu
        
        print(f"📥 Loading TTS model ({model_name})...")
        self.tts = TTS(model_name=model_name, gpu=gpu)
        print(f"✅ TTS model loaded")
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str
    ) -> str:
        """
        Synthesize text to speech and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file (WAV)
            
        Returns:
            str: Path to saved audio file
        """
        print(f"🔊 Synthesizing: {text[:100]}...")
        
        # Synthesize
        self.tts.tts_to_file(
            text=text,
            file_path=output_path
        )
        
        print(f"✅ Audio saved to: {output_path}")
        return output_path
    
    def synthesize_to_bytes(
        self,
        text: str,
        sample_rate: int = 22050
    ) -> bytes:
        """
        Synthesize text to speech and return as bytes.
        
        Args:
            text: Text to synthesize
            sample_rate: Desired sample rate
            
        Returns:
            bytes: PCM audio bytes
        """
        # Synthesize to numpy array
        wav = self.tts.tts(text=text)
        
        # Convert to int16 PCM
        wav_int16 = (np.array(wav) * 32767).astype(np.int16)
        
        return wav_int16.tobytes()


# Global instance
_coqui_tts: Optional[CoquiTTS] = None


def get_coqui_tts(model_name: str = "tts_models/en/ljspeech/tacotron2-DDC") -> CoquiTTS:
    """
    Get or create global Coqui TTS instance.
    
    Args:
        model_name: TTS model name
        
    Returns:
        CoquiTTS: TTS engine instance
    """
    global _coqui_tts
    if _coqui_tts is None:
        _coqui_tts = CoquiTTS(model_name=model_name)
    return _coqui_tts
