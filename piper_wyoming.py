"""
Wyoming protocol client for Piper TTS.
"""
import socket
import json
import wave
import io
import base64
import os
import logging
import time
import sys
import subprocess

logger = logging.getLogger("PiperWyoming")

class PiperWyomingClient:
    """Client for communicating with the Wyoming Piper TTS server."""
    
    def __init__(self, host="localhost", port=10200):
        """
        Initialize the Wyoming client.
        
        Args:
            host: Hostname or IP address of the Wyoming server
            port: Port number of the Wyoming server
        """
        self.host = host
        self.port = port
        
    def synthesize(self, text, output_file=None, speaker_id=0, debug=False):
        """
        Synthesize speech from text and save to an output file.
        
        Args:
            text: The text to synthesize
            output_file: Path to the output WAV file (or None to generate a path)
            speaker_id: Speaker ID for multi-speaker models (default: 0)
            debug: Enable debug logging
            
        Returns:
            A tuple of (success, message)
        """
        if not text:
            return False, "Empty text provided"
        
        # Generate an output filename if not provided
        if output_file is None:
            # Create a safe filename from the text (first 30 chars)
            safe_text = "".join([c if c.isalnum() else "_" for c in text[:30]])
            output_file = os.path.join("output", f"{safe_text}.wav")
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Try direct Docker approach for Windows to avoid encoding issues
        if sys.platform == "win32":
            return self._synthesize_via_docker(text, output_file, speaker_id, debug)
        else:
            # On Linux/macOS, try the Wyoming protocol first
            success, message = self._synthesize_via_wyoming(text, output_file, speaker_id, debug)
            if not success:
                # Fall back to direct Docker approach if Wyoming fails
                return self._synthesize_via_docker(text, output_file, speaker_id, debug)
            return success, message
    
    def _synthesize_via_wyoming(self, text, output_file, speaker_id=0, debug=False):
        """Use Wyoming protocol to communicate with Piper"""
        try:
            # Connect to the Wyoming server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)  # Set timeout to 10 seconds
            
            if debug:
                print(f"Connecting to {self.host}:{self.port}...")
                
            s.connect((self.host, self.port))
            
            # Send synthesis request
            request = {
                "type": "synthesize",
                "data": {
                    "text": text,
                    "speaker": str(speaker_id)
                }
            }
            
            if debug:
                print(f"Sending request: {json.dumps(request)}")
                
            # Add newline to separate JSON objects
            s.sendall(json.dumps(request).encode('utf-8') + b"\n")
            
            # New approach: Read the raw response in binary mode
            audio_data = bytearray()
            
            # We'll use a simple state machine to parse the response
            # State 0: Looking for JSON response
            # State 1: Collecting audio data
            state = 0
            buffer = bytearray()
            
            try:
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        if debug:
                            print("Connection closed by server")
                        break
                    
                    if debug:
                        print(f"Received {len(chunk)} bytes")
                    
                    # Look for JSON responses (they should be UTF-8 encoded and end with newline)
                    if state == 0:
                        buffer.extend(chunk)
                        newline_pos = buffer.find(b'\n')
                        
                        while newline_pos >= 0:
                            line = buffer[:newline_pos]
                            buffer = buffer[newline_pos + 1:]
                            
                            try:
                                # Decode line as UTF-8 (safer than default encoding)
                                json_str = line.decode('utf-8')
                                if debug:
                                    print(f"Processing JSON: {json_str[:100]}...")
                                
                                response = json.loads(json_str)
                                
                                if response["type"] == "audio":
                                    if debug:
                                        print("Received audio data")
                                    try:
                                        # Get audio data from base64
                                        audio_chunk = base64.b64decode(response["data"]["audio"])
                                        audio_data.extend(audio_chunk)
                                    except Exception as e:
                                        if debug:
                                            print(f"Error decoding audio: {e}")
                                
                                elif response["type"] == "error":
                                    return False, f"Server error: {response['data'].get('text', 'Unknown error')}"
                                
                                elif response["type"] == "end":
                                    if debug:
                                        print("End of audio stream")
                                    state = 1  # Done processing
                                    break
                                    
                            except UnicodeDecodeError as e:
                                if debug:
                                    print(f"Unicode error (trying to continue): {e}")
                                # Skip this chunk and continue
                                pass
                            except json.JSONDecodeError as e:
                                if debug:
                                    print(f"JSON error (trying to continue): {e}")
                                # Skip this chunk and continue
                                pass
                            
                            # Look for next newline
                            newline_pos = buffer.find(b'\n')
                    
                    # If we're done processing JSON or buffer is too large, break
                    if state == 1 or len(buffer) > 100000:
                        break
                
            except socket.timeout:
                if debug:
                    print("Socket timeout while reading")
            
            s.close()
            
            # If we didn't get any audio data, return error
            if not audio_data:
                return False, "No audio data received from server"
            
            # Save audio to WAV file
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(22050)  # Default for most Piper models
                wf.writeframes(audio_data)
            
            return True, f"Speech generated successfully and saved to {output_file}"
            
        except ConnectionRefusedError:
            return False, f"Could not connect to Wyoming server at {self.host}:{self.port}"
        except socket.timeout:
            return False, f"Connection to {self.host}:{self.port} timed out"
        except Exception as e:
            return False, f"Failed to synthesize via Wyoming: {str(e)}"
    
    def _synthesize_via_docker(self, text, output_file, speaker_id=0, debug=False):
        """Use direct Docker commands to generate speech"""
        try:
            if debug:
                print("Using direct Docker approach...")
            
            # Clean the text for shell usage
            clean_text = text.replace("'", "'\\''")
            
            # Create a temporary file for the raw audio
            temp_raw = os.path.join("output", "temp.raw")
            
            # Run piper directly in the container
            cmd = [
                "docker", "exec", "piper-tts",
                "sh", "-c", 
                f"echo '{clean_text}' | "
                f"/usr/share/piper/piper "
                f"--model /config/models/tts/en_US-joe-medium.onnx "
                f"--output_raw > /tmp/output.raw"
            ]
            
            if debug:
                print(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                if debug:
                    print(f"Command failed: {result.stderr}")
                return False, f"Direct command failed: {result.stderr}"
            
            # Copy the raw audio file from the container
            cmd_copy = [
                "docker", "cp", 
                "piper-tts:/tmp/output.raw", 
                temp_raw
            ]
            
            if debug:
                print(f"Copying file: {' '.join(cmd_copy)}")
            
            result_copy = subprocess.run(cmd_copy, capture_output=True, text=True)
            
            if result_copy.returncode != 0:
                if debug:
                    print(f"Copy failed: {result_copy.stderr}")
                return False, f"Failed to copy output: {result_copy.stderr}"
            
            # Read the raw audio
            if not os.path.exists(temp_raw):
                return False, f"Raw audio file not created: {temp_raw}"
                
            with open(temp_raw, "rb") as f:
                audio_data = f.read()
            
            if debug:
                print(f"Read {len(audio_data)} bytes from raw file")
                
            if not audio_data:
                return False, "No audio data in raw file"
            
            # Save as WAV file
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(22050)  # Default for most Piper models
                wf.writeframes(audio_data)
            
            # Clean up temp file
            try:
                os.remove(temp_raw)
            except:
                pass
                
            return True, f"Speech generated successfully and saved to {output_file}"
            
        except Exception as e:
            return False, f"Failed to synthesize via Docker: {str(e)}"
