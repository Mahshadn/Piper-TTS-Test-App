"""
Code Integration Example for Dockerized Piper TTS

This file demonstrates how to integrate the Wyoming Piper client
into a PyQt5 application like the original app.py.

The key benefit is cross-platform compatibility with Docker.
"""
import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import the Wyoming client
from piper_wyoming import PiperWyomingClient

class SynthesisThread(QThread):
    """Thread for running speech synthesis in the background."""
    update_progress = pyqtSignal(int)
    synthesis_complete = pyqtSignal(str, bool, str)
    
    def __init__(self, client, text, model_name, output_file, speaker_id=None):
        super().__init__()
        self.client = client
        self.text = text
        self.model_name = model_name
        self.output_file = output_file
        self.speaker_id = speaker_id
    
    def run(self):
        """Run the synthesis process."""
        self.update_progress.emit(10)
        success, message = self.client.synthesize(
            self.text, self.output_file, self.speaker_id
        )
        self.update_progress.emit(100)
        self.synthesis_complete.emit(self.model_name, success, message)


class DockerPiperApp(QMainWindow):
    """Example application using Dockerized Piper TTS."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize the Wyoming client
        self.piper_client = PiperWyomingClient(host="localhost", port=10200)
        self.threads = []  # Keep track of running threads
        
        # Set available models - these should match docker-compose.yml
        self.available_models = ["en_US-joe-medium", "en_US-libritts_r-medium"]
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Docker Piper TTS Example")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Input text area
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to convert to speech...")
        self.text_input.setText("Hello, this is a test of the Docker Piper text-to-speech system.")
        main_layout.addWidget(self.text_input)
        
        # Models section
        self.model_widgets = {}
        
        for model_name in self.available_models:
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
            play_button.setEnabled(False)
            play_button.clicked.connect(lambda checked, mn=model_name: self.play_audio(mn))
            model_layout.addWidget(play_button)
            
            # Store widgets
            self.model_widgets[model_name] = {
                "progress_bar": progress_bar,
                "play_button": play_button,
                "output_file": None
            }
            
            main_layout.addLayout(model_layout)
        
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
        for model_info in self.model_widgets.values():
            model_info["progress_bar"].setValue(0)
            model_info["play_button"].setEnabled(False)
            model_info["output_file"] = None
        
        # Start synthesis for each model
        for model_name in self.model_widgets:
            # Generate output filename
            safe_text = "".join([c if c.isalnum() else "_" for c in text[:30]])
            output_file = os.path.join("output", f"{safe_text}_{model_name}.wav")
            self.model_widgets[model_name]["output_file"] = output_file
            
            # Create and start the synthesis thread
            thread = SynthesisThread(
                self.piper_client, 
                text, 
                model_name, 
                output_file,
                speaker_id=0  # Default speaker ID
            )
            thread.update_progress.connect(
                lambda value, mn=model_name: self.update_progress(mn, value)
            )
            thread.synthesis_complete.connect(self.synthesis_complete)
            
            self.threads.append(thread)
            thread.start()
    
    def update_progress(self, model_name, value):
        """Update the progress bar for a model."""
        if model_name in self.model_widgets:
            self.model_widgets[model_name]["progress_bar"].setValue(value)
    
    def synthesis_complete(self, model_name, success, message):
        """Handle completion of synthesis for a model."""
        if model_name in self.model_widgets:
            # Set progress to 100% and enable play button if successful
            self.model_widgets[model_name]["progress_bar"].setValue(100)
            self.model_widgets[model_name]["play_button"].setEnabled(success)
            
            # Show error message if needed
            if not success:
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
        # Clean up threads
        self.threads = [thread for thread in self.threads if thread.isRunning()]
        
        # Re-enable buttons
        self.synthesize_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Show completion message
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
    
    def play_audio(self, model_name):
        """Play the generated audio file for a model."""
        output_file = self.model_widgets[model_name]["output_file"]
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
                import subprocess
                subprocess.run(["open", output_file], check=True)
            else:  # Linux and other Unix-like systems
                import subprocess
                subprocess.run(["xdg-open", output_file], check=True)
        except Exception as e:
            QMessageBox.warning(
                self, "Playback Error", 
                f"Failed to play audio file: {str(e)}"
            )


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = DockerPiperApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
