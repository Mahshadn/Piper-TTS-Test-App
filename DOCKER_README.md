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
2. Rename and place them in the `models/tts/` directory:
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

### 5. Integrating with Your Application

You can use the `PiperWyomingClient` class from `piper_wyoming.py` in your application:

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

## Controlling the Docker Container

- **Stop the container**: `docker-compose down`
- **View logs**: `docker-compose logs`
- **Restart**: `docker-compose restart`

## Changing Voice Models

Edit the `docker-compose.yml` file to change the default voice:

```yaml
environment:
  - PIPER_VOICE=en_US-libritts_r-medium  # Change to the voice you want
```

Then restart the container with `docker-compose restart`.

## Troubleshooting

1. **Container not starting**: Check Docker logs with `docker-compose logs`
2. **Connection refused**: Make sure the container is running with `docker ps`
3. **No audio output**: Verify that the voice models are in the correct location
4. **Voice model not found**: Make sure the model name in `docker-compose.yml` matches the filename in the `models/tts` directory

## How It Works

This setup runs Piper TTS in a Docker container and exposes it via the Wyoming protocol on port 10200. Your application communicates with it over this network interface, which works the same way on both Windows and Linux.
