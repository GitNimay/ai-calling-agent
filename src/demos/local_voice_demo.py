"""
Local voice demo for testing Gemini Live API audio streaming.
Demonstrates: WAV file → Gemini Live API → WAV file output
"""
import asyncio
import sys
import wave
import io
from pathlib import Path
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent.gemini_client import get_gemini_client

try:
    import soundfile as sf
    import librosa
    HAS_AUDIO_LIBS = True
except ImportError:
    HAS_AUDIO_LIBS = False
    print("Warning: soundfile and librosa not installed. Install with: pip install soundfile librosa")


def create_test_audio(output_path: str = "input.wav"):
    """
    Create a simple test audio file (sine wave tone).
    
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
    
    print(f"✅ Test audio created: {output_path} (2 seconds, 440Hz tone)")


def load_wav_as_pcm(wav_path: str) -> tuple[bytes, int]:
    """
    Load WAV file and convert to PCM bytes.
    
    Args:
        wav_path: Path to WAV file
        
    Returns:
        tuple: (pcm_bytes, sample_rate)
    """
    if not HAS_AUDIO_LIBS:
        # Fallback: read directly if already 16kHz mono
        with wave.open(wav_path, 'rb') as wf:
            if wf.getnchannels() != 1 or wf.getframerate() != 16000:
                raise ValueError("Without librosa, input must be mono 16kHz WAV")
            pcm_bytes = wf.readframes(wf.getnframes())
            return pcm_bytes, 16000
    
    # Use librosa to load and resample to 16kHz
    print(f"📁 Loading audio from: {wav_path}")
    y, sr = librosa.load(wav_path, sr=16000, mono=True)
    
    # Convert to PCM bytes
    buffer = io.BytesIO()
    sf.write(buffer, y, sr, format='RAW', subtype='PCM_16')
    buffer.seek(0)
    pcm_bytes = buffer.read()
    
    print(f"✅ Loaded {len(pcm_bytes)} bytes of PCM audio at {sr}Hz")
    return pcm_bytes, sr


def save_pcm_as_wav(pcm_bytes: bytes, output_path: str, sample_rate: int = 24000):
    """
    Save PCM bytes as WAV file.
    
    Args:
        pcm_bytes: Raw PCM audio bytes
        output_path: Path to save WAV file
        sample_rate: Sample rate (default: 24000 for Gemini output)
    """
    print(f"💾 Saving audio to: {output_path}")
    
    with wave.open(output_path, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    
    print(f"✅ Saved {len(pcm_bytes)} bytes as {output_path} ({sample_rate}Hz)")


async def main():
    """Run the local voice demo."""
    print("=" * 70)
    print("🎙️  AI Calling Agent - Local Voice Demo")
    print("=" * 70)
    print()
    
    # Check for input file
    input_file = "input.wav"
    if not Path(input_file).exists():
        print(f"⚠️  No input file found: {input_file}")
        print("Creating a test audio file...")
        create_test_audio(input_file)
        print()
    
    # Initialize Gemini client
    try:
        print("🔌 Connecting to Gemini Live API...")
        client = get_gemini_client()
        print(f"✅ Connected to Gemini ({client.live_model})")
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
    
    # Send to Gemini and get response
    try:
        print("🤖 Sending audio to Gemini Live API...")
        print("   (This may take a few seconds...)")
        
        pcm_output = await client.stream_audio_to_gemini(
            audio_pcm=pcm_input,
            system_instruction="You are a helpful AI assistant. Respond in a friendly tone.",
            sample_rate=input_rate
        )
        
        print(f"✅ Received {len(pcm_output)} bytes of audio response")
        print()
    except Exception as e:
        print(f"❌ Error processing audio: {e}")
        return
    
    # Save output
    try:
        output_file = "output.wav"
        save_pcm_as_wav(pcm_output, output_file, sample_rate=24000)
        print()
        print("=" * 70)
        print(f"✅ SUCCESS! Audio response saved to: {output_file}")
        print("=" * 70)
        print()
        print("🔊 Play the output file to hear Gemini's voice response!")
        print(f"   On Windows: start {output_file}")
        print(f"   On Linux: aplay {output_file}")
        print(f"   On Mac: afplay {output_file}")
        
    except Exception as e:
        print(f"❌ Error saving output: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
