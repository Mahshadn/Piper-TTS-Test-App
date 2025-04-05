# Piper TTS Test App

A simple application to test Piper TTS with different voice models. Supports both native and Docker-based deployments.

## Project Structure

- `app.py`: Main Python GUI application using PyQt5
- `piper_utils.py`: Utility functions for working with native Piper TTS
- `piper_wyoming.py`: Client for Dockerized Piper TTS using Wyoming protocol
- `test_wyoming.py`: Test script for the Docker setup
- `code_integration_guide.py`: Example of integrating Docker TTS with PyQt5
- `docker-compose.yml`: Docker configuration for Piper TTS
- `models/tts/`: Directory to store voice models
- `output/`: Directory where output audio files are saved
- `run.bat`: Windows batch file to run the native application

## Deployment Options

This project supports two deployment methods:

### 1. Native Mode (Original)

Run Piper directly on your system without Docker. Good for Windows development. See the original README below for details.

### 2. Docker Mode (Cross-Platform)

Run Piper in a Docker container, which works on both Windows and Linux. This is the recommended approach for production.

**To use Docker mode:**
1. Download voice models as described below
2. Follow instructions in [DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md)
3. Start with `docker-compose up -d`
4. Test with `python test_wyoming.py`

The Docker approach provides better cross-platform compatibility and isolates dependencies.

---

## Original README Content

### Prerequisites

- Python 3.8 or newer
- Piper TTS extracted locally (not installed via pip)
- Voice models placed in the `/models/tts/` directory

### Voice Models

This application is configured to work with the following voice models:
- en_US-joe-medium
- en_US-libritts_r-medium

Make sure these model files are placed in the `/models/tts/` directory as shown:
```
/models/tts/
  ├── en_US-joe-medium.onnx
  ├── en_US-joe-medium.onnx.json
  ├── en_US-libritts_r-medium.onnx
  └── en_US-libritts_r-medium.onnx.json
```

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/Mahshadn/Piper-TTS-Test-App.git
   cd Piper-TTS-Test-App
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\\Scripts\\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install the required Python dependencies:
   ```
   pip install -r requirements.txt
   ```

### Piper TTS Setup

1. Download Piper TTS:
   - Go to [https://github.com/rhasspy/piper/releases](https://github.com/rhasspy/piper/releases)
   - Download the appropriate version for your platform (e.g., `piper_windows_amd64.tar.gz` for 64-bit Windows)

2. Extract the Piper TTS archive:
   - Extract it either into the Piper-TTS-Test-App directory or a location in your PATH
   
3. Ensure the piper executable can be found:
   - If extracted to the project directory, the app will automatically find it
   - Otherwise, edit `app.py` to specify the path to the piper executable

4. Download voice models:
   - Go to [https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US)
   - Download `joe-medium.onnx`, `joe-medium.onnx.json`, `libritts_r-medium.onnx`, and `libritts_r-medium.onnx.json`
   - Rename them to `en_US-joe-medium.onnx`, `en_US-joe-medium.onnx.json`, `en_US-libritts_r-medium.onnx`, and `en_US-libritts_r-medium.onnx.json`
   - Place them in the `models/tts/` directory

### Usage

1. Run the application:
   ```
   python app.py
   ```
   
   Or on Windows, double-click the `run.bat` file.

2. Enter the text you want to convert to speech.

3. The application will generate audio files using both voice models for comparison.

4. The output files will be saved in the `output` directory.

## Docker Support

This project now includes Docker support for cross-platform compatibility. Instead of installing Piper natively on each platform, you can run it in a Docker container.

See the [DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md) for full details on setting up and using the Docker deployment option.

## Troubleshooting

### Native Mode Issues

If the application cannot find the Piper executable:

1. Make sure the Piper executable (`piper.exe` on Windows) is either:
   - In the same directory as `app.py`
   - In a parent directory
   - In your system PATH

2. You can manually specify the path to the Piper executable by modifying this line in `app.py`:
   ```python
   self.piper = PiperTTS(piper_executable="path/to/piper.exe")
   ```

3. Check the log file `piper_app.log` for any errors.

### Docker Mode Issues

See the Troubleshooting section in [DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md) for Docker-specific issues and solutions.
