import base64
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class CryptoError(Exception):
    pass

import contextvars
from contextlib import contextmanager

_request_cache = contextvars.ContextVar("request_cache", default=None)
_active_salt = contextvars.ContextVar("active_salt", default=None)

@contextmanager
def key_cache_context():
    """Context manager to cache derived keys and reuse salt within a single request context."""
    existing_cache = _request_cache.get()
    if existing_cache is not None:
        yield
        return

    salt = get_random_bytes(16)
    token_salt = _active_salt.set(salt)
    token_cache = _request_cache.set({})
    try:
        yield
    finally:
        _active_salt.reset(token_salt)
        _request_cache.reset(token_cache)

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from password and salt."""
    cache = _request_cache.get()
    if cache is not None:
        cache_key = (password, salt)
        if cache_key in cache:
            return cache[cache_key]
        key = PBKDF2(password, salt, dkLen=32, count=1000000)
        cache[cache_key] = key
        return key
    return PBKDF2(password, salt, dkLen=32, count=1000000)

def encrypt_message(message: str, password: str) -> str:
    """
    Encrypt a message using AES-256-GCM.
    Returns a base64 encoded string containing: salt + nonce + tag + ciphertext
    """
    try:
        salt = _active_salt.get()
        if salt is None:
            salt = get_random_bytes(16)
            
        key = derive_key(password, salt)
        
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
        
        # Combine all parts: salt (16) + nonce (16) + tag (16) + ciphertext
        combined = salt + cipher.nonce + tag + ciphertext
        return base64.b64encode(combined).decode('utf-8')
    except Exception as e:
        raise CryptoError(f"Encryption failed: {str(e)}")

def decrypt_message(encrypted_payload: str, password: str) -> str:
    """
    Decrypt a message using AES-256-GCM.
    Expects a base64 encoded string: salt + nonce + tag + ciphertext
    """
    try:
        data = base64.b64decode(encrypted_payload)
        
        if len(data) < 48:  # 16 (salt) + 16 (nonce) + 16 (tag)
            raise CryptoError("Invalid encrypted payload")
            
        salt = data[:16]
        nonce = data[16:32]
        tag = data[32:48]
        ciphertext = data[48:]
        
        key = derive_key(password, salt)
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        
        return decrypted_data.decode('utf-8')
    except (ValueError, KeyError):
        raise CryptoError("Decryption failed: Invalid password or corrupted data")
    except Exception as e:
        raise CryptoError(f"Decryption failed: {str(e)}")

if __name__ == "__main__":
    # Quick Test
    pwd = "test-password"
    msg = "Hello StegaVault!"
    
    enc = encrypt_message(msg, pwd)
    print(f"Encrypted: {enc}")
    
    dec = decrypt_message(enc, pwd)
    print(f"Decrypted: {dec}")
    
    assert msg == dec
    print("Verification Successful!")
