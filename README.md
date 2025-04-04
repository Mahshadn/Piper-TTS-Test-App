# Piper TTS Test App

A simple Windows application to test Piper TTS with different voice models.

## Prerequisites

- Python 3.8 or newer
- Piper TTS installed locally (see https://github.com/rhasspy/piper)
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

2. Install the required Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Make sure you have Piper TTS installed on your system.

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Enter the text you want to convert to speech.

3. The application will generate audio files using both voice models for comparison.

4. The output files will be saved in the `output` directory.

## Project Structure

- `app.py`: Main Python script with GUI interface
- `piper_utils.py`: Utility functions for working with Piper TTS
- `requirements.txt`: Required Python packages
- `models/tts/`: Directory to store voice models
- `output/`: Directory where output audio files are saved