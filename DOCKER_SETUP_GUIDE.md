# Piper TTS Docker Setup Guide

This comprehensive guide explains how to set up Piper TTS in Docker for cross-platform compatibility between Windows and Linux systems.

## Overview

There are several challenges when running Piper TTS in Docker across platforms:

1. **Binary compatibility**: The Piper executable is platform-specific
2. **File path differences**: Windows and Linux handle paths differently
3. **Protocol incompatibilities**: The Wyoming protocol can have encoding issues on Windows
4. **Docker implementation differences**: Docker Desktop (Windows) vs Docker Engine (Linux)

This solution addresses all of these by using a combination of:
- A pre-built Docker image from linuxserver.io
- Platform-specific code paths for maximum compatibility
- Direct Docker command execution as a fallback mechanism

## Quick Setup

### 1. Prerequisites

- Docker installed (Docker Desktop for Windows, Docker Engine for Linux)
- Python 3.6 or newer
- Voice models in the correct location

### 2. Files Required

- `docker-compose.yml`: Configures the Docker container
- `piper_wyoming.py`: Client code to interact with Piper TTS
- Voice models in `models/tts/` directory

### 3. Start Docker Container

```bash
docker-compose up -d
```

### 4. Test the Setup

```bash
python test_wyoming.py
```

## Technical Implementation

### 1. Docker Container Configuration

The `docker-compose.yml` file:

```yaml
version: '3'

services:
  piper:
    image: linuxserver/piper:latest
    container_name: piper-tts
    volumes:
      - ./models:/config/models  # Mount models directory
      - ./output:/output         # Mount output directory
    environment:
      - PIPER_VOICE=en_US-joe-medium  # Default voice
      - PIPER_SPEAKER=0               # Default speaker ID
    ports:
      - "10200:10200"                 # Wyoming protocol port
    restart: unless-stopped
```

Key points:
- Uses the maintained `linuxserver/piper` image which includes Wyoming protocol support
- Maps local directories into the container for models and output
- Exposes port 10200 for the Wyoming protocol server

### 2. Cross-Platform Client Implementation

The client (`piper_wyoming.py`) has two methods to generate speech:

1. **Wyoming Protocol Method**: Used first on Linux, connects to port 10200
2. **Direct Docker Method**: Used on Windows and as fallback on Linux, executes commands directly in the container

This architecture ensures maximum compatibility by:
- Using the path of least resistance for each platform
- Providing a fallback mechanism when the primary method fails
- Handling different encoding requirements per platform

### 3. Windows-Specific Workarounds

Windows has specific issues with the Wyoming protocol due to encoding differences. The solution:

1. Detect Windows platform: `if sys.platform == "win32"`
2. Skip Wyoming protocol on Windows and go straight to direct Docker commands
3. Use `subprocess.run()` to execute commands in the container
4. Generate audio directly in the container
5. Copy the file out using `docker cp`
6. Convert the raw audio to WAV format

This bypasses the encoding issues entirely by avoiding socket-based communication.

### 4. Voice Models Setup

The container expects voice models in a specific location:

```
models/
  tts/
    en_US-joe-medium.onnx
    en_US-joe-medium.onnx.json
```

These are mounted inside the container at `/config/models/tts/`.

## How It Works

When you call `piper_wyoming.py`:

1. On **Linux**:
   - First attempts to use Wyoming protocol over port 10200
   - If that fails, falls back to direct Docker command execution

2. On **Windows**:
   - Skips Wyoming protocol (avoids encoding issues)
   - Uses direct Docker command execution:
     ```python
     # The command executed inside the container
     echo 'TEXT' | /usr/share/piper/piper --model /config/models/tts/en_US-joe-medium.onnx --output_raw > /tmp/output.raw
     ```
   - Copies the raw audio out of the container
   - Converts it to a WAV file

## Integrating with Your Application

To use this in your own application:

```python
from piper_wyoming import PiperWyomingClient

# Initialize the client
piper = PiperWyomingClient()

# Generate speech
success, message = piper.synthesize("Text to speak", "output/audio.wav")
```

The client automatically handles platform differences, so your application code remains the same on both Windows and Linux.

## Troubleshooting

### Common Issues

1. **"No audio data received"**:
   - Check that voice models are in the correct location
   - Verify the voice name in `docker-compose.yml` matches your model files

2. **Container not starting**:
   - Check Docker logs: `docker-compose logs`
   - Ensure Docker is running

3. **Encoding errors**:
   - This is expected on Windows with Wyoming protocol
   - The code should automatically use the direct method instead

4. **Performance issues**:
   - The direct Docker command method is slightly slower than Wyoming protocol
   - For batch processing, consider using a Linux environment for better performance

### Checking Container Status

```bash
# See if container is running
docker ps | grep piper-tts

# Check container logs
docker-compose logs

# Enter container for debugging
docker exec -it piper-tts bash
```

## Implementation Details

### Wyoming Protocol

The Wyoming protocol is a JSON-based protocol for voice assistants:

1. Send a JSON request with text: `{"type": "synthesize", "data": {"text": "Hello world", "speaker": "0"}}`
2. Receive JSON responses with audio data: `{"type": "audio", "data": {"audio": "base64data..."}}`

The protocol is simple but can have encoding issues on Windows, especially with binary data.

### Direct Docker Method

The direct method:
1. Executes Piper directly in the container
2. Generates raw audio data
3. Copies the file out using Docker's copy command
4. Converts to WAV format locally

This is more reliable across platforms but slightly slower.

## Advanced Customization

### Changing Voice Models

To use different voice models:

1. Place the new model files in `models/tts/`
2. Update the `PIPER_VOICE` environment variable in `docker-compose.yml`
3. Restart the container: `docker-compose restart`

### Multi-Speaker Models

For multi-speaker models:

1. Set the speaker ID in the `synthesize()` method:
   ```python
   client.synthesize(text, output_file, speaker_id=1)
   ```
2. Or change the default in `docker-compose.yml`:
   ```yaml
   environment:
     - PIPER_SPEAKER=1
   ```

## Credits

- [Piper TTS](https://github.com/rhasspy/piper) by Rhasspy
- [linuxserver/piper](https://github.com/linuxserver/docker-piper) Docker image
