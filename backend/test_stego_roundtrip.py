"""
test_stego_roundtrip.py — Round-trip steganography tests.

Verifies that messages containing HTML/shell special characters
survive encrypt → hide → extract → decrypt byte-for-byte intact.
sanitize_input() was formerly applied to the message before encryption,
which silently transformed '<', '>', '&', '"', "'" into HTML entities
and broke the round-trip for any message containing those characters.
"""
import sys
import os
import tempfile
import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import stego
import audio_stego
import crypto

PASSWORD = "TestPassw0rd!Round"

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def make_png(w: int = 200, h: int = 200) -> str:
    """Create a temporary solid-colour PNG and return its path."""
    path = os.path.join(tempfile.gettempdir(), f"stego_test_input_{os.getpid()}.png")
    data = np.full((h, w, 3), 128, dtype=np.uint8)
    Image.fromarray(data).save(path)
    return path


def make_wav(duration_s: float = 1.0, sample_rate: int = 44100) -> str:
    """Create a minimal WAV file and return its path."""
    import wave, struct
    path = os.path.join(tempfile.gettempdir(), f"stego_test_input_{os.getpid()}.wav")
    n_samples = int(sample_rate * duration_s)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)          # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{n_samples}h", *([0] * n_samples)))
    return path


def stego_roundtrip_image(message: str) -> str:
    """Encrypt → hide in PNG → extract → decrypt. Returns recovered plaintext."""
    src = make_png()
    dst = os.path.join(tempfile.gettempdir(), f"stego_test_output_{os.getpid()}.png")
    try:
        ciphertext = crypto.encrypt_message(message, PASSWORD)
        stego.hide_message(src, ciphertext, dst)
        recovered_cipher = stego.extract_message(dst)
        return crypto.decrypt_message(recovered_cipher, PASSWORD)
    finally:
        for p in (src, dst):
            if os.path.exists(p):
                os.remove(p)


def stego_roundtrip_audio(message: str) -> str:
    """Encrypt → hide in WAV → extract → decrypt. Returns recovered plaintext."""
    src = make_wav()
    dst = os.path.join(tempfile.gettempdir(), f"stego_test_output_{os.getpid()}.wav")
    try:
        ciphertext = crypto.encrypt_message(message, PASSWORD)
        audio_stego.hide_message(src, ciphertext, dst)
        recovered_cipher = audio_stego.extract_message(dst)
        return crypto.decrypt_message(recovered_cipher, PASSWORD)
    finally:
        for p in (src, dst):
            if os.path.exists(p):
                os.remove(p)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #

def test_image_plain_message():
    """Baseline: plain ASCII message round-trips correctly."""
    msg = "StegaVault_2024"
    result = stego_roundtrip_image(msg)
    assert result == msg, f"Expected {msg!r}, got {result!r}"
    print(f"  ✅ plain ASCII image round-trip")


def test_image_special_chars():
    """
    HTML special characters must survive the round-trip unchanged.
    Previously sanitize_input() would turn  < → &lt;  > → &gt; etc.,
    causing the recovered plaintext to differ from the original.
    """
    msg = "<script>alert('XSS')</script> & \"quoted\" O'Reilly '};alert(1)//"
    result = stego_roundtrip_image(msg)
    assert result == msg, (
        f"Round-trip FAILED — messages differ:\n"
        f"  original : {msg!r}\n"
        f"  recovered: {result!r}"
    )
    print(f"  ✅ special-char image round-trip: {msg!r}")


def test_image_unicode():
    """Unicode / emoji survive round-trip (encrypted as UTF-8)."""
    msg = "密码库 🔐 Sécurité 日本語テスト"
    result = stego_roundtrip_image(msg)
    assert result == msg, f"Unicode round-trip FAILED: {result!r}"
    print(f"  ✅ unicode image round-trip")


def test_image_whitespace_only():
    """
    A whitespace-only message after .strip() is empty.
    The endpoint rejects it; at the crypto layer it's still a valid non-empty
    string, so we test that the strip logic is separate from HTML-escaping.
    """
    # Directly: the embed endpoint would reject this, but crypto itself is fine.
    msg = "  valid after strip  "
    expected = msg          # crypto does NOT strip — only the endpoint does
    result = stego_roundtrip_image(msg)
    assert result == expected, f"Whitespace round-trip FAILED: {result!r}"
    print(f"  ✅ whitespace-padded image round-trip")


def test_audio_special_chars():
    """Same special-character test for WAV audio steganography."""
    msg = "<b>Bold & 'quoted'</b> -- \"hello\" > world"
    result = stego_roundtrip_audio(msg)
    assert result == msg, (
        f"Audio round-trip FAILED — messages differ:\n"
        f"  original : {msg!r}\n"
        f"  recovered: {result!r}"
    )
    print(f"  ✅ special-char audio round-trip: {msg!r}")


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    print("\n🚀 Stego Round-Trip Test Suite\n")
    tests = [
        test_image_plain_message,
        test_image_special_chars,
        test_image_unicode,
        test_image_whitespace_only,
        test_audio_special_chars,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {t.__name__}: {e}")
        except Exception as e:
            print(f"  💥 {t.__name__} raised unexpected error: {e}")

    total = len(tests)
    print(f"\n{'✨ ALL' if passed == total else '⚠️ PARTIAL'} TESTS PASSED: {passed}/{total}\n")
    sys.exit(0 if passed == total else 1)
