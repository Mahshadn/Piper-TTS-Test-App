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
            s.sendall(json.dumps(request).encode() + b"\n")
            
            # Receive and process response
            audio_data = bytearray()
            buffer = bytearray()
            
            # Wait for response with timeout
            start_time = time.time()
            timeout = 30  # 30 seconds timeout
            
            while (time.time() - start_time) < timeout:
                try:
                    chunk = s.recv(4096)
                    if not chunk:
                        if debug:
                            print("Connection closed by server")
                        break
                    
                    if debug:
                        print(f"Received {len(chunk)} bytes")
                        
                    buffer.extend(chunk)
                    
                    # Process complete lines in the buffer
                    while b"\n" in buffer:
                        line_end = buffer.find(b"\n")
                        line = bytes(buffer[:line_end])
                        buffer = buffer[line_end + 1:]
                        
                        if line:
                            if debug:
                                print(f"Processing line: {line[:100]}...")
                                
                            try:
                                response = json.loads(line)
                                
                                if debug:
                                    print(f"Response type: {response['type']}")
                                
                                if response["type"] == "audio":
                                    # Decode base64 audio data
                                    audio_bytes = base64.b64decode(response["data"]["audio"])
                                    audio_data.extend(audio_bytes)
                                    
                                elif response["type"] == "error":
                                    return False, f"Server error: {response['data'].get('text', 'Unknown error')}"
                                    
                                elif response["type"] == "end":
                                    # End of audio stream
                                    if debug:
                                        print("End of audio stream")
                                    break
                                    
                            except json.JSONDecodeError as e:
                                if debug:
                                    print(f"Failed to parse JSON: {e}, Line: {line[:100]}...")
                                continue
                    
                    # If we received end signal, break out of the loop
                    if response.get("type") == "end":
                        break
                        
                except socket.timeout:
                    if debug:
                        print("Socket timeout, retrying...")
                    continue
            
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
            return False, f"Failed to synthesize speech: {str(e)}"
