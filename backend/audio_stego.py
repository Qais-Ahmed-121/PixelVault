import wave
import numpy as np
import os

class AudioStegoError(Exception):
    """Custom exception for Audio Steganography errors."""
    pass

def hide_message(audio_path: str, secret_message: str, output_path: str):
    """
    Hide a secret message in a WAV audio file using LSB steganography.
    Supports only .wav files (PCM format).
    """
    try:
        # Load WAV file
        with wave.open(audio_path, 'rb') as audio:
            params = audio.getparams()
            frames = audio.readframes(audio.getnframes())
            # Convert bytes to a mutable array (unsigned 8-bit or signed 16-bit)
            # We treat frames as a byte array for simple LSB manipulation
            frame_bytes = bytearray(frames)

        # Prepare message
        msg_bytes = secret_message.encode('utf-8')
        msg_len = len(msg_bytes)

        # Header: 32 bits for the length of the message
        # Convert length to 32-bit big-endian bits
        header_bits = np.unpackbits(np.array([msg_len], dtype='>u4').view(np.uint8))
        
        # Message bits
        message_bits = np.unpackbits(np.frombuffer(msg_bytes, dtype=np.uint8))
        
        all_bits = np.concatenate([header_bits, message_bits])

        # Capacity check
        if len(all_bits) > len(frame_bytes):
            raise AudioStegoError(f"Message too large for audio file. Capacity: {len(frame_bytes) // 8} bytes, Required: {len(all_bits) // 8} bytes.")

        # Embed bits in the LSB of each byte of the audio frames
        for i in range(len(all_bits)):
            # Clear the LSB (mask with 254 / 0xFE) and OR with the bit
            frame_bytes[i] = (frame_bytes[i] & 254) | all_bits[i]

        # Save the new WAV file
        with wave.open(output_path, 'wb') as output_audio:
            output_audio.setparams(params)
            output_audio.writeframes(frame_bytes)

    except Exception as e:
        if isinstance(e, AudioStegoError):
            raise e
        raise AudioStegoError(f"Failed to hide message in audio: {str(e)}")

def extract_message(audio_path: str) -> str:
    """
    Extract a hidden message from a WAV audio file.
    Reads the 32-bit header first to determine message length.
    """
    try:
        with wave.open(audio_path, 'rb') as audio:
            frames = audio.readframes(audio.getnframes())
            frame_bytes = bytearray(frames)

        # Extract header (first 32 bits)
        header_bits = np.array([frame_bytes[i] & 1 for i in range(32)], dtype=np.uint8)
        msg_len = np.packbits(header_bits).view('>u4')[0]

        if msg_len == 0 or msg_len > (len(frame_bytes) - 32) // 8:
            raise AudioStegoError("No valid hidden message found in audio or file corrupted.")

        # Extract message bits
        total_message_bits = msg_len * 8
        message_bits = np.array([frame_bytes[i] & 1 for i in range(32, 32 + total_message_bits)], dtype=np.uint8)
        
        # Convert bits back to bytes
        msg_bytes = np.packbits(message_bits).tobytes()
        return msg_bytes.decode('utf-8')

    except Exception as e:
        if isinstance(e, AudioStegoError):
            raise e
        raise AudioStegoError(f"Failed to extract message from audio: {str(e)}")

if __name__ == "__main__":
    # Standalone Test Script
    test_input = "test_audio.wav"
    test_output = "stego_audio.wav"
    
    # Create a dummy WAV file for testing if it doesn't exist
    import struct
    import math

    def create_dummy_wav(filename):
        sample_rate = 44100
        duration = 1.0  # 1 second
        frequency = 440.0
        n_samples = int(sample_rate * duration)
        
        with wave.open(filename, 'w') as wav:
            wav.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
            for i in range(n_samples):
                value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                wav.writeframes(struct.pack('<h', value))

    print("Generating dummy test WAV...")
    create_dummy_wav(test_input)
    
    secret = "PixelVault_Audio_Test_2024_TopSecret"
    print(f"Original Secret: {secret}")
    
    try:
        hide_message(test_input, secret, test_output)
        print(f"Message hidden in {test_output}")
        
        extracted = extract_message(test_output)
        print(f"Extracted Secret: {extracted}")
        
        assert secret == extracted
        print("Audio Steganography Successful!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        for f in [test_input, test_output]:
            if os.path.exists(f): os.remove(f)
