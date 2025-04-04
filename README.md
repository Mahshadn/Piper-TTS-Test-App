# Piper TTS Test App

A simple Windows application to test Piper TTS with different voice models.

## Prerequisites

- Python 3.8 or newer
- Piper TTS extracted locally (not installed via pip)
- Voice models placed in the `/models/tts/` directory

## Voice Models

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

## Installation

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
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install the required Python dependencies:
   ```
   pip install -r requirements.txt
   ```

## Piper TTS Setup

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

## Usage

1. Run the application:
   ```
   python app.py
   ```
   
   Or on Windows, double-click the `run.bat` file.

2. Enter the text you want to convert to speech.

3. The application will generate audio files using both voice models for comparison.

4. The output files will be saved in the `output` directory.

## Project Structure

- `app.py`: Main Python script with GUI interface
- `piper_utils.py`: Utility functions for working with Piper TTS
- `requirements.txt`: Required Python packages
- `models/tts/`: Directory to store voice models
- `output/`: Directory where output audio files are saved
- `run.bat`: Windows batch file to run the application

## Troubleshooting

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
