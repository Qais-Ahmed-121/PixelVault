import cv2
import numpy as np
import os

class VideoStegoError(Exception):
    """Custom exception for Video Steganography errors."""
    pass

def hide_message(video_path: str, secret_message: str, output_path: str):
    """
    Hide a secret message in a video using frame-based LSB steganography.
    The message is distributed across the pixels of the video frames.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoStegoError("Could not open video file.")

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        fourcc = cv2.VideoWriter_fourcc(*'FFV1') # Lossless codec is crucial for steganography

        # Prepare message bits
        msg_bytes = secret_message.encode('utf-8')
        msg_len = len(msg_bytes)
        header_bits = np.unpackbits(np.array([msg_len], dtype='>u4').view(np.uint8))
        message_bits = np.unpackbits(np.frombuffer(msg_bytes, dtype=np.uint8))
        all_bits = np.concatenate([header_bits, message_bits])

        # Capacity check
        total_pixels = width * height * 3 # RGB channels
        # We'll check capacity across the whole video potentially, but for simplicity
        # let's see if it fits in the frames available.
        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if len(all_bits) > total_pixels * num_frames:
             raise VideoStegoError("Message too large for video capacity.")

        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        bit_index = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if bit_index < len(all_bits):
                # Flatten the frame to inject bits
                flat_frame = frame.flatten()
                
                # Calculate how many bits we can fit in this frame
                bits_to_hide = min(len(all_bits) - bit_index, flat_frame.size)
                
                # Embed bits: Clear LSB and OR with message bit
                current_bits = all_bits[bit_index:bit_index + bits_to_hide]
                flat_frame[:bits_to_hide] = (flat_frame[:bits_to_hide] & 0xFE) | current_bits
                
                frame = flat_frame.reshape((height, width, 3))
                bit_index += bits_to_hide
            
            out.write(frame)

        cap.release()
        out.release()

    except Exception as e:
        if isinstance(e, VideoStegoError):
            raise e
        raise VideoStegoError(f"Failed to hide message in video: {str(e)}")

def extract_message(video_path: str) -> str:
    """
    Extract a hidden message from a video file.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoStegoError("Could not open video file.")

        # 1. Extract Header (first 32 bits from first frame)
        ret, frame = cap.read()
        if not ret:
            raise VideoStegoError("Could not read video frames.")
        
        flat_first_frame = frame.flatten()
        header_bits = flat_first_frame[:32] & 1
        msg_len = np.packbits(header_bits).view('>u4')[0]

        if msg_len == 0:
            raise VideoStegoError("No valid hidden message found.")

        # 2. Extract Message Bits
        total_bits_needed = 32 + (msg_len * 8)
        bits_collected = []
        
        # Reset capture to start
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        while len(bits_collected) < total_bits_needed:
            ret, frame = cap.read()
            if not ret:
                break
            
            flat_frame = frame.flatten()
            bits_to_take = min(total_bits_needed - len(bits_collected), flat_frame.size)
            bits_collected.extend(flat_frame[:bits_to_take] & 1)

        cap.release()
        
        if len(bits_collected) < total_bits_needed:
            raise VideoStegoError("Video ended before full message could be extracted.")

        # Remove header bits and convert to message
        message_bits = np.array(bits_collected[32:], dtype=np.uint8)
        msg_bytes = np.packbits(message_bits).tobytes()
        return msg_bytes.decode('utf-8')

    except Exception as e:
        if isinstance(e, VideoStegoError):
            raise e
        raise VideoStegoError(f"Failed to extract message from video: {str(e)}")

if __name__ == "__main__":
    # Standalone Test Script (requires a small input video)
    test_input = "test_video.mp4"
    test_output = "stego_video.avi" # Use .avi with FFV1 for lossless
    
    # Create a small dummy video for testing
    print("Generating dummy test video...")
    height, width = 100, 100
    fps = 24
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Temporary input source
    out = cv2.VideoWriter(test_input, fourcc, fps, (width, height))
    
    for i in range(fps * 2): # 2 seconds
        frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        out.write(frame)
    out.release()

    secret = "PixelVault_Video_LSB_2024_FrameByFrame"
    print(f"Original Secret: {secret}")
    
    try:
        hide_message(test_input, secret, test_output)
        print(f"Message hidden in {test_output}")
        
        extracted = extract_message(test_output)
        print(f"Extracted Secret: {extracted}")
        
        assert secret == extracted
        print("Video Steganography Successful!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        for f in [test_input, test_output]:
            if os.path.exists(f): os.remove(f)
