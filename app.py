#!/usr/bin/env python3
"""
Piper TTS Test Application

A simple GUI to test different Piper TTS voice models.
"""
import os
import sys
import logging
from typing import Dict, List, Optional
import subprocess
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QComboBox, QGroupBox,
    QFileDialog, QMessageBox, QProgressBar, QSlider, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from piper_utils import PiperTTS, get_output_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('piper_app.log')
    ]
)
logger = logging.getLogger("PiperApp")

# Create output directory if it doesn't exist
os.makedirs("output", exist_ok=True)


class SynthesisThread(QThread):
    """Thread for running speech synthesis in the background."""
    update_progress = pyqtSignal(int)
    synthesis_complete = pyqtSignal(str, bool, str)
    
    def __init__(self, piper: PiperTTS, text: str, model_name: str, 
                 output_file: str, speaker_id: Optional[int] = None):
        super().__init__()
        self.piper = piper
        self.text = text
        self.model_name = model_name
        self.output_file = output_file
        self.speaker_id = speaker_id
    
    def run(self):
        """Run the synthesis process."""
        self.update_progress.emit(10)
        success, message = self.piper.synthesize(
            self.text, self.model_name, self.output_file, self.speaker_id
        )
        self.update_progress.emit(100)
        self.synthesis_complete.emit(self.model_name, success, message)


class PiperTTSApp(QMainWindow):
    """Main application window for Piper TTS testing."""
    
    def __init__(self, piper_executable=None):
        super().__init__()
        
        # Initialize Piper TTS with optional executable path
        self.piper = PiperTTS(piper_executable=piper_executable)
        self.threads = []  # Keep track of running threads
        
        self.available_models = self.piper.list_models()
        
        if not self.available_models:
            QMessageBox.warning(
                self, "No Models Found", 
                "No Piper TTS models found in the 'models/tts' directory. "
                "Please make sure you have the voice models installed correctly."
            )
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Piper TTS Test App")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Input text group
        input_group = QGroupBox("Input Text")
        input_layout = QVBoxLayout()
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to convert to speech...")
        self.text_input.setText("Hello, this is a test of the Piper text-to-speech system.")
        
        input_layout.addWidget(self.text_input)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Models group
        models_group = QGroupBox("Voice Models")
        models_layout = QVBoxLayout()
        
        # List of selected models to process
        self.model_checkboxes = {}
        
        # Only include models shown in the screenshot
        target_models = ["en_US-joe-medium", "en_US-libritts_r-medium"]
        
        for model_name in self.available_models:
            # Skip models not in our target list
            if model_name not in target_models:
                continue
                
            model_layout = QHBoxLayout()
            
            # Model name label
            model_label = QLabel(model_name)
            model_layout.addWidget(model_label)
            
            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            model_layout.addWidget(progress_bar)
            
            # Play button
            play_button = QPushButton("Play")
            play_button.setEnabled(False)  # Disabled until synthesis is complete
            play_button.clicked.connect(lambda checked, mn=model_name: self.play_audio(mn))
            model_layout.addWidget(play_button)
            
            # Store the widgets for this model
            self.model_checkboxes[model_name] = {
                "progress_bar": progress_bar,
                "play_button": play_button,
                "output_file": None  # Will be set after synthesis
            }
            
            models_layout.addLayout(model_layout)
        
        models_group.setLayout(models_layout)
        main_layout.addWidget(models_group)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.synthesize_button = QPushButton("Synthesize All")
        self.synthesize_button.clicked.connect(self.synthesize_all)
        control_layout.addWidget(self.synthesize_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_all)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(control_layout)
    
    def synthesize_all(self):
        """Synthesize speech for all selected models."""
        # Get the input text
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Empty Text", "Please enter some text to synthesize.")
            return
        
        # Disable the synthesize button and enable the stop button
        self.synthesize_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Reset progress bars and play buttons
        for model_info in self.model_checkboxes.values():
            model_info["progress_bar"].setValue(0)
            model_info["play_button"].setEnabled(False)
            model_info["output_file"] = None
        
        # Start synthesis for each model
        for model_name in self.model_checkboxes:
            # Generate output filename
            output_file = get_output_filename(text, model_name)
            self.model_checkboxes[model_name]["output_file"] = output_file
            
            # Create and start the synthesis thread
            thread = SynthesisThread(self.piper, text, model_name, output_file)
            thread.update_progress.connect(
                lambda value, mn=model_name: self.update_progress(mn, value)
            )
            thread.synthesis_complete.connect(self.synthesis_complete)
            
            self.threads.append(thread)
            thread.start()
    
    def update_progress(self, model_name: str, value: int):
        """Update the progress bar for a model."""
        if model_name in self.model_checkboxes:
            self.model_checkboxes[model_name]["progress_bar"].setValue(value)
    
    def synthesis_complete(self, model_name: str, success: bool, message: str):
        """Handle completion of synthesis for a model."""
        if model_name in self.model_checkboxes:
            # Set progress to 100% and enable play button if successful
            self.model_checkboxes[model_name]["progress_bar"].setValue(100)
            self.model_checkboxes[model_name]["play_button"].setEnabled(success)
            
            # Log the result
            if success:
                logger.info(f"Synthesis completed for {model_name}: {message}")
            else:
                logger.error(f"Synthesis failed for {model_name}: {message}")
                QMessageBox.warning(
                    self, "Synthesis Failed", 
                    f"Failed to synthesize speech for {model_name}:\n{message}"
                )
        
        # Check if all threads are done
        all_done = all(not thread.isRunning() for thread in self.threads)
        if all_done:
            self.synthesis_complete_all()
    
    def synthesis_complete_all(self):
        """Handle completion of all synthesis tasks."""
        # Clean up the threads list
        self.threads = [thread for thread in self.threads if thread.isRunning()]
        
        # Re-enable the synthesize button and disable the stop button
        self.synthesize_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Show a completion message
        QMessageBox.information(
            self, "Synthesis Complete", 
            "Speech synthesis is complete for all models."
        )
    
    def stop_all(self):
        """Stop all running synthesis threads."""
        # Terminate all running threads
        for thread in self.threads:
            if thread.isRunning():
                thread.terminate()
                thread.wait()
        
        # Clear the threads list
        self.threads = []
        
        # Re-enable the synthesize button and disable the stop button
        self.synthesize_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Show a message
        QMessageBox.information(
            self, "Synthesis Stopped", 
            "Speech synthesis has been stopped."
        )
    
    def play_audio(self, model_name: str):
        """Play the generated audio file for a model."""
        output_file = self.model_checkboxes[model_name]["output_file"]
        if not output_file or not os.path.exists(output_file):
            QMessageBox.warning(
                self, "File Not Found", 
                f"Audio file for {model_name} not found."
            )
            return
        
        # Use the operating system's default audio player
        try:
            if sys.platform == "win32":
                os.startfile(output_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", output_file], check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", output_file], check=True)
        except Exception as e:
            QMessageBox.warning(
                self, "Playback Error", 
                f"Failed to play audio file: {str(e)}"
            )


def main():
    """Main entry point for the application."""
    # You can specify the path to the piper executable here if needed
    # piper_executable = "path/to/piper.exe"  # Uncomment and modify if needed
    piper_executable = None  # Auto-detect
    
    app = QApplication(sys.argv)
    window = PiperTTSApp(piper_executable)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
