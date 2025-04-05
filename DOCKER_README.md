# Piper TTS Docker Setup

This guide explains how to run Piper TTS using Docker, which works cross-platform on both Windows and Linux.

## Prerequisites

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine (Linux)
2. Voice models in the `models/tts` directory (same as the non-Docker setup)

## Setup Instructions

### 1. Pull the Repository

Clone or pull the latest changes from the repository:

```
git pull origin main
```

### 2. Download Voice Models

If you haven't already, download the voice models as described in the main README:

1. Download from [Hugging Face](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US)
2. Place them in the `models/tts/` directory:
   - `en_US-joe-medium.onnx`
   - `en_US-joe-medium.onnx.json`
   - `en_US-libritts_r-medium.onnx`
   - `en_US-libritts_r-medium.onnx.json`

### 3. Start the Docker Container

Run the Docker container using Docker Compose:

```
docker-compose up -d
```

This starts the Piper TTS service in the background. The first time you run this, it will download the container image which may take a few minutes.

### 4. Test the TTS Service

Run the test script to verify the service is working:

```
python test_wyoming.py
```

This will:
1. Connect to the Piper TTS service running in Docker
2. Generate a test audio file in the `output` directory
3. Attempt to play the file (if possible)

## Troubleshooting

If you encounter issues, try these steps:

1. **Check container logs**:
   ```
   docker-compose logs
   ```

2. **Verify your model directory structure**:
   Make sure your models are in the right place. The directory structure should be:
   ```
   models/
     tts/
       en_US-joe-medium.onnx
       en_US-joe-medium.onnx.json
   ```

3. **Check container is running**:
   ```
   docker ps
   ```
   You should see the `piper-tts` container running.

4. **Restart the container**:
   ```
   docker-compose down
   docker-compose up -d
   ```

5. **Run with debug mode**:
   The test script has been updated to provide more diagnostic information. It will show what's happening during the communication with the server.

6. **Common issues**:
   - Voice model not found: Verify that the model name in docker-compose.yml matches your voice file name
   - No audio output: Check that the model files are correctly named and located
   - Connection refused: Make sure Docker is running and the container has started

## How It Works

The setup uses the Wyoming protocol, which is a simple JSON-based protocol for speech services:

1. The Docker container runs Piper TTS with the Wyoming server
2. Your application sends text to the server over a network socket
3. The server processes the text with the specified voice model
4. The server returns audio data which is saved to a WAV file

## Using in Your Application

You can integrate the `PiperWyomingClient` class from `piper_wyoming.py` into your application:

```python
from piper_wyoming import PiperWyomingClient

# Initialize the client
piper = PiperWyomingClient()

# Synthesize speech
success, message = piper.synthesize(
    "Text to convert to speech", 
    output_file="output/example.wav"
)
```

## Integrating with Your Existing App

To integrate with your existing PyQt5 application, you can:

1. Import the Wyoming client:
```python
from piper_wyoming import PiperWyomingClient
```

2. Initialize it in your app:
```python
self.piper_wyoming = PiperWyomingClient()
```

3. Replace your existing TTS calls with:
```python
success, message = self.piper_wyoming.synthesize(text, output_file)
```

This provides a Docker-based TTS backend that works consistently across platforms.
