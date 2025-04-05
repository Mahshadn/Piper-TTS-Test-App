"""
Test script for Wyoming Piper TTS client.
"""
import os
import sys
import subprocess
from piper_wyoming import PiperWyomingClient

def main():
    """Main entry point for the test script."""
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Initialize the Wyoming client
    client = PiperWyomingClient(host="localhost", port=10200)
    
    # Test text to synthesize
    test_text = "Hello, this is a test of the Piper Text-to-Speech system running in Docker."
    
    # Synthesize speech
    output_file = os.path.join("output", "docker_test.wav")
    success, message = client.synthesize(test_text, output_file)
    
    # Print the result
    if success:
        print(f"Success: {message}")
        
        # Try to play the audio file
        try:
            if sys.platform == "win32":
                os.startfile(output_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", output_file], check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", output_file], check=True)
        except Exception as e:
            print(f"Note: Could not automatically play the audio file: {str(e)}")
            print(f"The file is available at: {os.path.abspath(output_file)}")
    else:
        print(f"Error: {message}")
        print("\nMake sure the Docker container is running with:")
        print("  docker-compose up -d")

if __name__ == "__main__":
    main()
