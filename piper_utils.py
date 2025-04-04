"""
Utility functions for working with Piper TTS.
"""
import os
import logging
import subprocess
import json
import sys
from typing import Dict, Optional, List, Tuple

class PiperTTS:
    """A wrapper for the Piper TTS command-line executable."""
    
    def __init__(self, models_dir: str = "./models/tts", piper_executable: str = None):
        """
        Initialize the PiperTTS class.
        
        Args:
            models_dir: Directory containing the voice model files
            piper_executable: Path to the piper executable (default: auto-detect)
        """
        self.models_dir = models_dir
        self.available_models = self._find_models()
        self.logger = logging.getLogger("PiperTTS")
        
        # Find the piper executable
        self.piper_executable = piper_executable
        if not self.piper_executable:
            self.piper_executable = self._find_piper_executable()
        
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
    
    def _find_piper_executable(self) -> str:
        """
        Find the piper executable.
        
        Returns:
            Path to the piper executable
        """
        # Check if piper is in the current directory
        if os.path.exists("piper"):
            return "./piper"
        elif os.path.exists("piper.exe"):
            return "./piper.exe"
        
        # Check if piper is in the PATH
        try:
            if sys.platform == "win32":
                # On Windows, check common locations
                potential_paths = [
                    "./piper.exe",
                    "../piper.exe",
                    "../../piper.exe",
                    "./piper/piper.exe",
                    "../piper/piper.exe"
                ]
                for path in potential_paths:
                    if os.path.exists(path):
                        return path
                
                # If not found, assume it's in the PATH
                return "piper.exe"
            else:
                # On Unix systems
                subprocess.run(["which", "piper"], check=True, stdout=subprocess.PIPE)
                return "piper"
        except (subprocess.SubprocessError, FileNotFoundError):
            self.logger.warning("Could not find piper in PATH. Please specify the path to the piper executable.")
            return "piper"  # Default to just "piper", hoping it's in the PATH
    
    def _find_models(self) -> Dict[str, str]:
        """
        Find all available voice models in the models directory.
        
        Returns:
            A dictionary mapping model names to their full paths
        """
        models = {}
        
        if not os.path.exists(self.models_dir):
            return models
        
        for filename in os.listdir(self.models_dir):
            if filename.endswith(".onnx"):
                model_name = os.path.splitext(filename)[0]
                model_path = os.path.join(self.models_dir, filename)
                
                # Check if the JSON config file also exists
                json_path = f"{model_path}.json"
                if os.path.exists(json_path):
                    models[model_name] = model_path
        
        return models
    
    def list_models(self) -> List[str]:
        """
        List all available voice models.
        
        Returns:
            A list of model names
        """
        return list(self.available_models.keys())
    
    def synthesize(self, text: str, model_name: str, output_file: str, 
                   speaker_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Synthesize speech using Piper TTS.
        
        Args:
            text: The input text to synthesize
            model_name: The name of the voice model to use
            output_file: The path to save the output audio file
            speaker_id: Speaker ID for multi-speaker models (if applicable)
            
        Returns:
            A tuple of (success, message)
        """
        if model_name not in self.available_models:
            return False, f"Model '{model_name}' not found. Available models: {', '.join(self.list_models())}"
        
        model_path = self.available_models[model_name]
        json_path = f"{model_path}.json"
        
        # Build the command
        cmd = [self.piper_executable, "--model", model_path, "--output_file", output_file]
        
        # Add speaker ID if provided
        if speaker_id is not None:
            cmd.extend(["--speaker", str(speaker_id)])
        
        # Check if model is multi-speaker from the JSON config
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    config = json.load(f)
                    if config.get('num_speakers', 1) > 1 and speaker_id is None:
                        # Multi-speaker model, but no speaker ID was provided
                        # Use the first speaker (0) by default
                        cmd.extend(["--speaker", "0"])
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Could not read model config file: {e}")
        
        # Run Piper TTS
        try:
            # Use Popen to pipe text to the process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send text to process
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                return False, f"Piper TTS failed with error: {stderr}"
            
            return True, f"Speech generated successfully and saved to {output_file}"
            
        except Exception as e:
            return False, f"Failed to run Piper TTS: {str(e)}"


def get_output_filename(text: str, model_name: str, output_dir: str = "output") -> str:
    """
    Generate a unique output filename based on the text and model name.
    
    Args:
        text: The input text
        model_name: The voice model name
        output_dir: Directory to save output files
        
    Returns:
        A file path for the output audio file
    """
    # Create a safe filename from the text (first 30 chars)
    safe_text = "".join([c if c.isalnum() else "_" for c in text[:30]])
    
    # Create the filename
    filename = f"{safe_text}_{model_name}.wav"
    
    # Full path
    file_path = os.path.join(output_dir, filename)
    
    return file_path
