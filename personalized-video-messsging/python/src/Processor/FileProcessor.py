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
    
    def load_csv_data(self, csv_path):
        """
        Load data from the CSV file into a list of dictionaries.
        
        Returns:
            List of dict objects loaded from the CSV file
        
        Raises:
            FileNotFoundError: If the CSV file does not exist
            ValueError: If the CSV file has invalid structure
        """
        
        print(f'Loading csv file at {csv_path}')
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        entries = []
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Verify required columns exist
            required_columns = ['video', 'text', 'voice_id', 'segment_start', 'segment_end', 'sync_mode', 'output_format','lipsync_model', 'tts_model']
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            for row in reader:
                entry = {
                    'video': row['video'],
                    'text': row['text'],
                    'voice_id': row.get('voice_id', ''),
                    'segment_start': row.get('segment_start',-1),
                    'segment_end': row.get('segment_end',-1),
                    'sync_mode': row.get('sync_mode','bounce'),
                    'output_format': row.get('output_format','mp4'),
                    'lipsync_model': row.get('lipsync_model','lipsync-2'),
                    'tts_model': row.get('tts_model','eleven_multilingual_v2')
                }
            
                entries.append(entry)
                
        return entries
    
    def write_dicts_to_csv(self, data, filename):
        """
        Write a list of dictionaries to a CSV file, where each dictionary key becomes a column header.
        
        Args:
            data (list): List of dictionaries with the same keys
            filename (str): Output CSV filename
        """
        if not data:
            print("No data to write.")
            return
        
        # Extract fieldnames from the first dictionary
        # fieldnames = set().union(*(d.keys() for d in data))
        fieldnames = ['video', 'text', 'audio', 'voice_id', 'lipsync_jobID', 'outputUrl']
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                # Create a CSV DictWriter object
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write the header row (keys as column headers)
                writer.writeheader()
                
                # Write each row with only the specified keys
                for row in data:
                    filtered_row = {key: row[key] for key in fieldnames}  # Filter the row to include only specified keys
                    writer.writerow(filtered_row)
                
            print(f"Successfully wrote {len(data)} rows to {filename}")
        
        except Exception as e:
            print(f"Error writing to CSV: {str(e)}")