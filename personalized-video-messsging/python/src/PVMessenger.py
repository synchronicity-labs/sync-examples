import os

from src.service.LipSyncService import LipSyncProcessor
from src.service.VoiceService import VoiceProcessor
from src.Processor.FileProcessor import FileProcessor


class PVMessenger:
    def __init__(self,
                root_dir: str,
                lipsync_api_key: str,
                elevenlabs_api_key: str
            ):
        
        self.root_dir = root_dir
        self.file_processor = FileProcessor(self.root_dir)
        self.lipsync_service = LipSyncProcessor(lipsync_api_key) 
        self.voice_service = VoiceProcessor(elevenlabs_api_key)

        print(f'Initialized the Lipsync & ElevenLabs services.') 
    
    def run(self, input_csv_path: str, output_csv_path: str):
        """
        Performs all the steps needed for generating personalized video messages like voice 
        cloning, TTS, lip-syncing.
        
        Args:
            csv_path (str): Path to the input csv
                
        Returns:
            str: Path to where the output csv is written
            
        Raises:
            requests.exceptions.RequestException: If the API requests, file downloads, uploads fail
        """
        # load the input csv file into a dict
        entries = self.file_processor.load_csv_data(input_csv_path)
        jobs = []
        # print(f'Loaded csv file at {input_csv_path} successfully')
        # clone voice using the first entry as the reference if no voice IDs specified in input csv
        if not entries[0]['voice_id']:
            print(f'No voice ID found, cloning voice using first entry as reference')
            temp_video = self.file_processor.download(entries[0]['video'])
            temp_audio = self.file_processor.extract_audio(temp_video)
            
            name = 'my_voice_clone'
            voice_id = self.voice_service.clone_voice(name, temp_audio)

            # cleanup temp video and audio files
            os.remove(temp_video)
            os.remove(temp_audio)
        
        for i, entry in enumerate(entries):
            # update voice_id in all entries
            if not entry['voice_id']:
                entry['voice_id'] = voice_id

            # generate speech using the voice ID and the text field from the csv, output is audio bytes
            # print(f"Generating speech for voice ID: {entry['voice_id']}, entry {i+1}")
            input_audio = self.voice_service.generate_speech(entry)
            
            # write the output in a temp mp3 file
            dir = f"Data/Inputs"
            full_path = os.path.join(self.root_dir, dir)
            os.makedirs(full_path, exist_ok=True)
            tmp_aud = os.path.join(full_path, f'gen_aud_{i}.mp3')
            
            with open(tmp_aud, "wb") as audio_file:
                audio_file.write(input_audio)
            
            # upload the temp file to a temp file hosting service and get the url
            aud_url = self.file_processor.upload_file_uguu(tmp_aud)
            
            if aud_url:
                print(f'Uploaded generated speech for entry {i+1} to {aud_url}')
                entry['audio'] = aud_url

                # post the lipsyncing request to the API endpoint
                response_json = self.lipsync_service.process_lip_sync(entry)
                print(f'Submitted lipsync job successfully for entry {i+1}, job ID: {response_json["id"]}') 
                jobs.append((i,response_json['id']))
                entry['lipsync_jobID'] = response_json['id']
            
            else:
                entry['audio'] = 'Generated speech upload error'

            # delete the generated speech temp audio file
            os.remove(tmp_aud)

        # poll for lipsync job status updates
        print(f'Polling for lipsync job completions...')
        lipsync_results = self.lipsync_service.poll_for_status(jobs)
        
        for res in lipsync_results:
            entries[res['idx']]['output_url'] = res['output_url']
        
        self.file_processor.write_dicts_to_csv(entries, output_csv_path)

        return output_csv_path
        