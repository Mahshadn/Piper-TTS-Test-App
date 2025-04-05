"""
Test script for Wyoming Piper TTS client.
"""
import os
import sys
import subprocess
import time
from piper_wyoming import PiperWyomingClient

def main():
    """Main entry point for the test script."""
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Check Docker container status
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}", "--filter", "name=piper-tts"],
            capture_output=True,
            text=True,
            check=True
        )
        container_running = "piper-tts" in result.stdout
    except Exception:
        container_running = False
        
    if not container_running:
        print("WARNING: Piper TTS container doesn't appear to be running.")
        print("Run 'docker-compose up -d' to start it.")
        restart = input("Would you like to try starting it now? (y/n): ")
        if restart.lower() == 'y':
            try:
                subprocess.run(["docker-compose", "up", "-d"], check=True)
                print("Starting container, please wait...")
                time.sleep(5)  # Give some time for container to start
            except Exception as e:
                print(f"Error starting container: {e}")
                return
    
    # Initialize the Wyoming client with debug mode
    client = PiperWyomingClient(host="localhost", port=10200)
    
    # Test text to synthesize
    test_text = "Hello, this is a test of the Piper Text-to-Speech system running in Docker."
    
    # Get container logs to help diagnose issues
    try:
        print("Checking Piper container logs...")
        log_result = subprocess.run(
            ["docker", "logs", "--tail", "20", "piper-tts"],
            capture_output=True,
            text=True
        )
        if "error" in log_result.stdout.lower() or "error" in log_result.stderr.lower():
            print("\nPossible issues found in container logs:")
            print(log_result.stdout)
            print(log_result.stderr)
    except Exception:
        pass
        
    # List available voice models in the container
    try:
        print("\nChecking for voice models in the container...")
        model_result = subprocess.run(
            ["docker", "exec", "piper-tts", "ls", "-la", "/config/models/tts"],
            capture_output=True,
            text=True
        )
        print(model_result.stdout)
    except Exception as e:
        print(f"Could not check voice models: {e}")
    
    print("\nAttempting to synthesize speech with debug info...")
    # Synthesize speech with debug info
    output_file = os.path.join("output", "docker_test.wav")
    success, message = client.synthesize(test_text, output_file, debug=True)
    
    # Print the result
    if success:
        print(f"\nSuccess: {message}")
        
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
        print(f"\nError: {message}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Docker is running")
        print("2. Check that the container is running: docker ps")
        print("3. Check container logs: docker-compose logs")
        print("4. Make sure voice models are in the correct location")
        print("5. Verify the path is set correctly in docker-compose.yml")
        print("6. Try restarting the container: docker-compose restart")

if __name__ == "__main__":
    main()
