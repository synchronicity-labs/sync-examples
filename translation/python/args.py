
class Args:
    SYNCLABS_API_KEY = ""
    ELEVENLABS_API_KEY = ""
    OPENAI_API_KEY = ""
    
    input_vid_url = "https://public-sync-test-files.s3.us-east-1.amazonaws.com/video-short.mp4"
    target_language = "Spanish"
    source_language = ""
    output_json_path = "output.json"

    lipsync_model = "lipsync-2"
    tts_model = "eleven_multilingual_v2"
    gpt_model = "gpt-3.5-turbo"
    transcription_model = "whisper-1"
    
    voice_id = ""
    sync_mode = "bounce"
    output_format = "mp4"
    segment_start = -1
    segment_end = -1