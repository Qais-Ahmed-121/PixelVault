# Steganography — PixelVault

---

## 1. Overview

PixelVault implements **Least Significant Bit (LSB)** steganography across three media formats. The core algorithm is consistent across all three: embed a 32-bit length header followed by the message bits into the LSB of each carrier byte.

All three modules share the same design:
- **Encrypt first** — the message is AES-256-GCM encrypted before embedding. The carrier only ever contains ciphertext.
- **Lossless output required** — output formats must be lossless to preserve embedded bits.
- **32-bit header** — encodes message byte length in big-endian format as the first 32 bits.

---

## 2. Supported Formats

| Type | Input Formats | Output Format | Codec |
|---|---|---|---|
| Image | PNG, JPG, JPEG | PNG | Lossless (PIL) |
| Audio | WAV (PCM only) | WAV | Preserved WAV params |
| Video | MP4, AVI | AVI | FFV1 (lossless) |

> **Critical:** Output must be lossless. JPEG compression, MP3 encoding, or lossy video codecs will destroy the embedded LSBs and make extraction impossible.

---

## 3. Algorithm — Image (`stego.py`)

### Embedding

```python
hide_message(image_path, secret_message, output_path)
```

1. Open image with Pillow → convert to NumPy array
2. Encode message to UTF-8 bytes
3. Build 32-bit big-endian header = `len(msg_bytes)`
4. Convert header + message to bit array with `np.unpackbits()`
5. Capacity check: `len(all_bits) <= img_array.size`
6. Flatten image array
7. For each bit: `flat_img[i] = (flat_img[i] & 0xFE) | bit`
8. Reshape → save as PNG

### Extraction

```python
extract_message(image_path) -> str
```

1. Open PNG → flatten pixel array
2. Extract first 32 bits → `np.packbits().view('>u4')[0]` = `msg_len`
3. Validate: `msg_len > 0` and `msg_len <= (size - 32) // 8`
4. Extract next `msg_len * 8` bits
5. Pack bits → bytes → decode UTF-8 → return ciphertext string

### Capacity

```
Capacity (bytes) = total_pixels / 8
```
A 100×100 RGB image has 30,000 pixels → ~3,750 bytes capacity.

---

## 4. Algorithm — Audio (`audio_stego.py`)

### Embedding

```python
hide_message(audio_path, secret_message, output_path)
```

1. Open WAV with `wave.open()` → read all frames as `bytearray`
2. Build header + message bits identical to image module
3. Capacity check: `len(all_bits) <= len(frame_bytes)`
4. For each bit: `frame_bytes[i] = (frame_bytes[i] & 0xFE) | bit`
5. Write output WAV with original parameters

### Extraction

```python
extract_message(audio_path) -> str
```

1. Read all WAV frames as `bytearray`
2. Extract 32-bit header from first 32 bytes (LSB of each byte)
3. Validate `msg_len`
4. Extract `msg_len * 8` bits → decode UTF-8 → return ciphertext

### Capacity

```
Capacity (bytes) = total_frame_bytes / 8
```
A 44100Hz mono 16-bit 1-second WAV = 88,200 frame bytes → ~11,025 bytes capacity.

### Limitations
- WAV only (PCM format) — compressed audio (MP3, AAC, OGG) is not supported.
- Modifying audio LSBs introduces imperceptible noise — inaudible at standard levels.

---

## 5. Algorithm — Video (`video_stego.py`)

### Embedding

```python
hide_message(video_path, secret_message, output_path)
```

1. Open with OpenCV `cv2.VideoCapture()`
2. Calculate capacity: `width * height * 3 * num_frames`
3. Build header + message bits
4. Create `cv2.VideoWriter` with FFV1 lossless codec (`.avi`)
5. Process frame by frame:
   - Flatten frame pixel array
   - Embed remaining bits into LSB of pixels
   - Reshape and write to output
6. Release capture + writer

### Extraction

```python
extract_message(video_path) -> str
```

1. Read first frame → extract 32-bit header
2. Calculate `total_bits_needed = 32 + (msg_len * 8)`
3. Reset capture to frame 0
4. Collect bits frame by frame until enough are gathered
5. Strip header bits → pack → decode → return ciphertext

### Capacity

```
Capacity (bytes) = (W × H × 3 × N_frames) / 8
```
A 100×100 RGB 24fps 2-second video = 6,000,000 bits → 750,000 bytes capacity.

### Limitations
- Input can be MP4 or AVI; output is always AVI with FFV1 codec.
- FFV1 requires the `ffv1` codec to be available in the OpenCV installation.
- Large video files will exceed the 5MB upload limit.

---

## 6. Validation & Error Handling

| Check | Module | Behavior |
|---|---|---|
| File size > 5MB | `main.py` (validate_file) | HTTP 413 |
| Wrong file extension | `main.py` (validate_file) | HTTP 400 |
| Message too large for carrier | stego modules | `StegoError` / `AudioStegoError` / `VideoStegoError` → HTTP 400 |
| No hidden message found | stego modules (extraction) | Custom exception → HTTP 400 |
| Wrong stego password | `crypto.decrypt_message()` | `CryptoError` → HTTP 400 |
| Corrupted carrier | stego extraction | Exception caught → HTTP 400 |
| Empty message | `main.py` | HTTP 400 `Message cannot be empty` |

---

## 7. Operation History

Every successful embed or extract operation creates a `StegoOperation` record. Embed operations also create a `MediaFile` record pointing to the saved output file in `uploads/`. Extract operations do not save output files.

The `GET /stego/history` endpoint returns all operations for the authenticated user. `GET /stego/download/{media_file_id}` allows re-downloading a previously generated stego file (if the file still exists on disk).
