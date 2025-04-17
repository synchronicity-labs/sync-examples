import os
import subprocess
import csv
import urllib.request
import requests


class FileProcessor():
    """
    Handles video downloading, audio extraction, handling of csv files.
    """
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
    
    def download(self, url: str) -> str:
        """Download files from URL and return the local file path."""
        
        dir = f"Data/Inputs"
        full_path = os.path.join(self.root_dir, dir)
        os.makedirs(full_path, exist_ok=True)
        local_filename = os.path.join(dir, os.path.basename(url))
        urllib.request.urlretrieve(url, local_filename)
        
        return local_filename
    
    def run_ffmpeg_command(self, command: str):
        process = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if process.returncode != 0:
            print(f"FFmpeg error: {process.stderr.decode()}")
            raise Exception("FFmpeg command failed for extracting audio")
        
    def extract_audio(self, video_path: str) -> str:
        """ Extract audio from video file using FFmpeg. """
                
        # Generate audio filename
        dir = f"Data/Inputs"
        file_name = os.path.basename(video_path)
        stem = os.path.splitext(file_name)[0]
        audio_filename = f"{stem}_audio.wav"
        audio_path = os.path.join(dir,audio_filename)
        
        # Construct FFmpeg command
        command = f"ffmpeg -i {video_path} -vn {audio_path}"
        self.run_ffmpeg_command(command)
        
        return audio_path

    def upload_file_uguu(self, file_path: str):
        """Upload a local file to uguu and get the url"""
    
        try:
            url = 'https://uguu.se/upload'
            with open(file_path, "rb") as audio_file: 
                data = [('files[]', audio_file)]
                response = requests.post(url, files=data)
            res = response.json()
            if res['success']:
                output = res['files'][0]['url']
                return output
            else:
                print(f"Error {res['errorcode']} during upload: {res['description']}")
               
        except Exception as e:
            print(f"Error during upload: {str(e)}")
            return None
        return None
    
    def check_required_keys(self, args_instance):
        # Define the required keys
        required_keys = {
            'SYNCLABS_API_KEY': 'Synclabs API key is required',
            'ELEVENLABS_API_KEY': 'ElevenLabs API key is required',
            'OPENAI_API_KEY': 'OpenAI API key is required',
            'input_vid_url': 'Input video URL is required',
            'target_language': 'Target language is required',
        }
        
        # Optional keys that need validation if they're being used
        conditional_keys = {
            'voice_id': '',
            'lipsync_model': 'lipsync-2',
            'tts_model': 'eleven_multilingual_v2',
            'gpt_model': 'gpt-3.5-turbo',
            'transcription_model': 'whisper-1',
            'source_language': '',
            "output_json_path": 'output.json',
            'sync_mode': "bounce",
            'segment_start': -1,
            'segment_end': -1
        }
                
        # Check required keys
        for key, message in required_keys.items():
            if not hasattr(args_instance, key) or getattr(args_instance, key) == "":
                raise ValueError(f'Missing field in args.py: {message}')
        
        # Update default values for conditional keys
        for key, value in conditional_keys.items():
            if not hasattr(args_instance, key) or getattr(args_instance, key) == "":
                args_instance.key = value
        
        return args_instance
