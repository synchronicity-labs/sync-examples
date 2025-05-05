import os
import requests
from typing import Dict, Optional, Any



class VoiceProcessor():
    """
    Handles voice services using wrapper around ElevenLabs.
    """
    def __init__(self, elevenlabs_api_key: str):  
        self.base_url = "https://api.elevenlabs.io/v1"
        self.api_key = elevenlabs_api_key
        self.headers = {
            "xi-api-key": elevenlabs_api_key,
            "Content-Type": "application/json"
        }
    
    def generate_speech(self, entry: Dict):
        """
        Generate speech from text using the specified voice.
        
        Args:
            text: Text to convert to speech
            voice_id: ID of the voice to use
            
        Returns:
            Audio bytes of the generated audio file
            
        Raises:
            ValueError: If text-to-speech generation fails
        """
        
        
        json_data = {
            "text": entry['text'],
            "model_id": entry['tts_model'],
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = self._make_request(
                "POST", 
                f"/text-to-speech/{entry['voice_id']}",
                json_data=json_data,
                headers=self.headers
            )
            return response.content
            
        except Exception as e:
            print(f"Speech generation failed: {e}")
            raise ValueError(f"Speech generation failed: {e}")
    
    def _make_request(self, method: str, endpoint: str, 
                      headers: Optional[Dict] = None, 
                      params: Optional[Dict[str, Any]] = None, 
                      data: Optional[Dict[str, Any]] = None,
                      files: Optional[Dict[str, Any]] = None,
                      json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make an HTTP request to the ElevenLabs API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint to call
            headers: Optional additional headers
            params: Optional URL parameters
            data: Optional form data
            files: Optional files to upload
            json_data: Optional JSON payload
            
        Returns:
            Response object from the requests library
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self.headers.copy()
        
        if headers:
            request_headers.update(headers)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                files=files,
                json=json_data
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    def clone_voice(self, name: str, reference_audio: str) -> str:
        """
        Clone a voice using a reference audio file.
        
        Args:
            name: Name for the cloned voice
            reference_audio: path of the reference audio file
            
        Returns:
            Voice ID of the cloned voice
            
        Raises:
            ValueError: If voice cloning fails
        """
        # print(f"Cloning voice from reference audio: {reference_audio}")
        
        # Prepare files for voice cloning
        
        files = {
            'files': open(reference_audio, 'rb'),
        }
        
        payload = {
            "name": name
        }
        
        try:
            response = requests.post(f'{self.base_url}/voices/add',files=files,data=payload, headers={"xi-api-key": self.api_key})
            voice_id = response.json().get('voice_id')
            
            if not voice_id:
                print(response.json())
                raise ValueError("Voice cloning response did not contain a voice_id")
                
            print(f"Successfully cloned voice with ID: {voice_id}")
            return voice_id   
        except Exception as e:
            print(f"Voice cloning failed: {e}")
            raise ValueError(f"Voice cloning failed: {e}")
        finally:
            # Close file handles 
            for file_obj in files.values():
                file_obj.close()
    
    