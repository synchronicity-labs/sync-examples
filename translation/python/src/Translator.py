import os
import pprint
import json

from src.service.LipSyncService import LipSyncProcessor
from src.service.VoiceService import VoiceProcessor
from src.service.TranslationService import TranslationProcessor
from src.utils.FileProcessor import FileProcessor


class Translator:
    def __init__(self,
                root_dir: str,
                args
            ):
        
        self.root_dir = root_dir
        self.file_processor = FileProcessor(self.root_dir)
        self.args = self.file_processor.check_required_keys(args)
        self.lipsync_service = LipSyncProcessor(self.args.SYNCLABS_API_KEY) 
        self.voice_service = VoiceProcessor(self.args.ELEVENLABS_API_KEY)
        self.translation_service = TranslationProcessor(self.args.OPENAI_API_KEY)

        print(f'Initialized the Lipsync, Translation, & ElevenLabs services.') 
    
    def run(self):
        """
        Performs all the steps needed for generating translated videos like translation, voice 
        cloning, TTS, lip-syncing.
        
        Raises:
            requests.exceptions.RequestException: If the API requests, file downloads, uploads fail
        """
        output = {'input_video': self.args.input_vid_url}
        # download the video to local filesystem
        self.args.input_video_path = self.file_processor.download(self.args.input_vid_url)
        # extract the audio from the input video file 
        temp_audio = self.file_processor.extract_audio(self.args.input_video_path)
        
        if not self.args.voice_id:
            # clone voice using extracted audio
            name = 'my_voice_clone'
            self.args.voice_id = self.voice_service.clone_voice(name, temp_audio)
        output['voice_id'] = self.args.voice_id
        
        # transcribe and translate the extracted audio 
        transcription = self.translation_service.transcribe(temp_audio, self.args.transcription_model)  
        translation = self.translation_service.translate(transcription, self.args)
        
        # generate speech using the voice ID and the translated text, output is audio bytes
        input_audio = self.voice_service.generate_speech(translation, self.args.voice_id)
        
        # write the output in a temp mp3 file
        dir = f"Data/Inputs"
        full_path = os.path.join(self.root_dir, dir)
        os.makedirs(full_path, exist_ok=True)
        tmp_aud = os.path.join(full_path, f'generated_speech.mp3')
        
        with open(tmp_aud, "wb") as audio_file:
            audio_file.write(input_audio)
        
        # upload the temp file to a temp file hosting service and get the url
        aud_url = self.file_processor.upload_file_uguu(tmp_aud)

        if aud_url:
            print(f'Uploaded generated speech to {aud_url}')
            output['generated_audio'] = aud_url
            self.args.aud_url = aud_url
            # post the lipsyncing request to the API endpoint
            response_json = self.lipsync_service.process_lip_sync(self.args)
            print(f'Submitted lipsync job successfully, job ID: {response_json["id"]}')
            output['lipsync_jobID'] = response_json["id"]
        else:
            print('Generated speech upload error')
            raise

        # poll for lipsync job status updates
        print(f'Polling for lipsync job completions...')
        lipsync_results = self.lipsync_service.poll_for_status([response_json['id']])
        
        for res in lipsync_results:
            output['output_url'] = res['output_url']
        
        pprint.pprint(output)

        # Write JSON to a file
        with open(self.args.output_json_path, 'w') as f:
            json.dump(output, f, indent=4)
        
        # cleanup temp files
        os.remove(temp_audio)
        os.remove(self.args.input_video_path)

        