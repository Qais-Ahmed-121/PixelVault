import numpy as np
from PIL import Image
import io
import os

class StegoError(Exception):
    pass

def msg_to_bits(msg_bytes: bytes) -> np.ndarray:
    """Convert bytes to a numpy array of bits."""
    bits = np.unpackbits(np.frombuffer(msg_bytes, dtype=np.uint8))
    return bits

def bits_to_msg(bits: np.ndarray) -> bytes:
    """Convert a numpy array of bits back to bytes."""
    msg_bytes = np.packbits(bits).tobytes()
    return msg_bytes

def hide_message(image_path: str, secret_message: str, output_path: str):
    """
    Hide a secret message in an image using LSB steganography.
    The message is first converted to bits, and its length is prefixed as a 32-bit header.
    """
    try:
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Prepare message
        msg_bytes = secret_message.encode('utf-8')
        msg_len = len(msg_bytes)
        
        # Header: 32 bits for the length of the message
        header_bits = np.unpackbits(np.array([msg_len], dtype='>u4').view(np.uint8))
        message_bits = msg_to_bits(msg_bytes)
        
        all_bits = np.concatenate([header_bits, message_bits])
        
        # Capacity check
        total_pixels = img_array.size
        if len(all_bits) > total_pixels:
            raise StegoError(f"Message too large for image. Capacity: {total_pixels // 8} bytes, Required: {len(all_bits) // 8} bytes.")
        
        # Flatten image array for easier bit manipulation
        flat_img = img_array.flatten()
        
        # Embed bits in LSB
        # Clear LSB (mask with 254 / 0xFE) and OR with message bit
        flat_img[:len(all_bits)] = (flat_img[:len(all_bits)] & 254) | all_bits
        
        # Reshape back to original image shape
        new_img_array = flat_img.reshape(img_array.shape)
        
        # Save as PNG to preserve LSBs (lossless)
        new_img = Image.fromarray(new_img_array.astype(np.uint8), mode=img.mode)
        new_img.save(output_path, "PNG")
        
    except Exception as e:
        if isinstance(e, StegoError):
            raise e
        raise StegoError(f"Failed to hide message: {str(e)}")

def extract_message(image_path: str) -> str:
    """
    Extract a hidden message from an image.
    Reads the 32-bit header first to determine message length.
    """
    try:
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img)
        flat_img = img_array.flatten()
        
        # Extract header (first 32 bits)
        header_bits = flat_img[:32] & 1
        msg_len = np.packbits(header_bits).view('>u4')[0]
        
        if msg_len == 0 or msg_len > (flat_img.size - 32) // 8:
             raise StegoError("No valid hidden message found or image corrupted.")
             
        # Extract message bits
        total_bits = msg_len * 8
        msg_bits = flat_img[32:32+total_bits] & 1
        
        msg_bytes = bits_to_msg(msg_bits)
        return msg_bytes.decode('utf-8')
        
    except Exception as e:
        if isinstance(e, StegoError):
            raise e
        raise StegoError(f"Failed to extract message: {str(e)}")

if __name__ == "__main__":
    # Test Script
    import tempfile
    
    # Create a dummy image
    test_img_path = "test_input.png"
    test_output_path = "test_stego.png"
    
    data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    Image.fromarray(data).save(test_img_path)
    
    secret = "PixelVault_Secret_Message_2024"
    print(f"Original Secret: {secret}")
    
    try:
        hide_message(test_img_path, secret, test_output_path)
        print(f"Message hidden in {test_output_path}")
        
        extracted = extract_message(test_output_path)
        print(f"Extracted Message: {extracted}")
        
        assert secret == extracted
        print("Steganography Successful!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_img_path): os.remove(test_img_path)
        if os.path.exists(test_output_path): os.remove(test_output_path)
