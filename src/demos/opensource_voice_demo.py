"""
Open-source voice demo using Whisper STT + Gemini + Coqui TTS.
Demonstrates: WAV file → Whisper → Gemini Text → Coqui TTS → WAV file
"""
import asyncio
import sys
import wave
from pathlib import Path
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent.gemini_client import get_gemini_client


def create_test_audio(output_path: str = "input.wav"):
    """
    Create a simple test audio file with a spoken message.
    
    Args:
        output_path: Path to save the test audio file
    """
    print(f"📝 Creating test audio file: {output_path}")
    
    # Generate a simple 2-second tone at 440Hz (A note)
    sample_rate = 16000
    duration = 2.0
    frequency = 440.0
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t)
    
    # Scale to 16-bit integer range
    audio = (audio * 32767).astype(np.int16)
    
    # Write WAV file
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    
    print(f"✅ Test audio created: {output_path}")


def load_wav_as_pcm(wav_path: str) -> tuple[bytes, int]:
    """
    Load WAV file and return PCM bytes.
    
    Args:
        wav_path: Path to WAV file
        
    Returns:
        tuple: (pcm_bytes, sample_rate)
    """
    print(f"📁 Loading audio from: {wav_path}")
    
    with wave.open(wav_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        pcm_bytes = wf.readframes(n_frames)
    
    print(f"✅ Loaded {len(pcm_bytes)} bytes at {sample_rate}Hz")
    return pcm_bytes, sample_rate


def save_pcm_as_wav(pcm_bytes: bytes, output_path: str, sample_rate: int = 22050):
    """
    Save PCM bytes as WAV file.
    
    Args:
        pcm_bytes: Raw PCM audio bytes
        output_path: Path to save WAV file
        sample_rate: Sample rate (Coqui TTS outputs at 22050Hz)
    """
    print(f"💾 Saving audio to: {output_path}")
    
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    
    print(f"✅ Saved audio: {output_path}")


async def main():
    """Run the open-source voice demo."""
    print("=" * 70)
    print("🎙️  AI Calling Agent - Open-Source Voice Demo")
    print("    Pipeline: Whisper STT → Gemini → Coqui TTS")
    print("=" * 70)
    print()
    
    # Check for input file
    input_file = "input_opensource.wav"
    if not Path(input_file).exists():
        print(f"⚠️  No input file found: {input_file}")
        print("You can record your own audio or create a test file.")
        print("For now, creating a test tone...")
        create_test_audio(input_file)
        print()
        print("⚠️  NOTE: The test tone won't produce meaningful transcription.")
        print("For best results, record yourself speaking a question.")
        print()
    
    # Initialize Gemini client
    try:
        print("🔌 Initializing AI agent...")
        client = get_gemini_client()
        print(f"✅ Gemini client ready")
        print()
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return
    
    # Load input audio
    try:
        pcm_input, input_rate = load_wav_as_pcm(input_file)
        print()
    except Exception as e:
        print(f"❌ Error loading audio: {e}")
        return
    
    # Process through open-source pipeline
    try:
        print("=" * 70)
        print("🔄 Processing through Open-Source Voice Pipeline...")
        print("=" * 70)
        print()
        
        pcm_output = await client.process_audio_opensource(
            audio_pcm=pcm_input,
            sample_rate=input_rate,
            system_instruction="You are a helpful AI assistant. Respond in a friendly and concise way."
        )
        
        print()
        print(f"✅ Pipeline complete! Received {len(pcm_output)} bytes")
        print()
    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Save output
    try:
        output_file = "output_opensource.wav"
        save_pcm_as_wav(pcm_output, output_file, sample_rate=22050)
        print()
        print("=" * 70)
        print(f"✅ SUCCESS! Audio saved to: {output_file}")
        print("=" * 70)
        print()
        print("🔊 Play the output to hear the AI's voice response!")
        print(f"   Windows: start {output_file}")
        print(f"   Linux:   aplay {output_file}")
        print(f"   Mac:     afplay {output_file}")
        print()
        print("💡 TIP: Record your own voice asking a question and save as")
        print(f"         '{input_file}' for more realistic results!")
        
    except Exception as e:
        print(f"❌ Error saving output: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
