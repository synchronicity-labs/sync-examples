# Translation

This is an example repository to show how to integrate Sync.so's LipSync API easily in your workflows. The example shown here is for creating lipsynced translated videos for a target language. For voice cloning and TTS, ElevenLabs is used. For transcription & translation, OpenAI is used.

## Prerequisites
Python 3.8+ is recommended for optimal performance and compatibility with all features.

Before running the code, ensure that you have the following:

- **Sync API key** for lipsyncing.
- **ElevenLabs API key** for TTS & voice cloning.
- **OpenAI API key** for transcription & translation.

## Setup and Usage

To get started, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Install required packages
    ```bash
    pip install -r requirements.txt
    ```

3. **Prepare the args.py file**:

- Fill in the `args.py` file with the required data. 
- You can specify a `voice_id` in the file. If left blank, the code will automatically clone the voice based on the audio in the video input.
- You can specify a `source_language` for better translation. If left blank, it will auto-detect and translate.

#### Default values:
If you don't specify values for lipsync, OpenAI, and TTS options in the `args.py`, the following default settings will be applied:
- `sync_mode`: `"bounce"`
- `output_format`: `"mp4"`
- `lipsync_model`: `"lipsync-2"`
- `tts_model`: `"eleven_multilingual_v2"`
- `transcription_model`: `"whisper-1"`
- `gpt_model`: `"gpt-3.5-turbo"`

4. **Update the API keys, video URL, target language**:

- Open the `args.py` file and insert your **Sync API key**, **OpenAI API key**, and **ElevenLabs API key**.
- Insert the URL to your input video in the same file.
- Type in the target language to which you want to translate the video to

5. **Run the application**:

- Execute the main.py script to generate the translated video:
    ```bash
    python main.py
    ```
For more details, refer to the official API documentation for both **Sync API** and **Elevenlabs API**

## Important Notes

- **Audio Requirement**: The video file must contain audio that will be used for voice cloning.

- **Language Support**: Refer to the ElevenLabs and OpenAI API docs for supported languages by the model you're using for cloning and translation respectively.

- **Temporary File Hosting**: This code uses the temporary file hosting service [Uguu](https://uguu.se/) to generate URLs for TTS audio files. These URLs are then used with the Sync API. By default, the uploaded URLs will be deleted after 3 hours. If you prefer to use your own file hosting service, modify the `upload_file_uguu()` function in `FileProcessor.py` to return a custom URL. The rest of the code should remain unaffected.

- **Translation Prompt**: Refer to the `system_prompt` var in `TranslationService.py` to look at the default prompt used for translation. You can edit and play around with this to get better results. 

- **Job Polling**: Currently, polling for lipsync job completion times out after 60 mins. The code will print all your job_ids in that eventuality. You can also increase/decrease the timeout limit by editing `timeout` arg in `poll_for_status()` function in the `LipSyncService.py`. To fetch output URLs after polling timeout, run the `fetch_updates.py` file which will use the `output_json_path`. 

## Aditional Resources

- [Sync API Documentation](https://docs.sync.so/introduction)
- [ElevenLabs API Documentation](https://elevenlabs.io/docs/api-reference/introduction)


We hope you find this repository useful for integrating translation into your workflow! If you have any questions or issues, feel free to open an issue in this repository.
