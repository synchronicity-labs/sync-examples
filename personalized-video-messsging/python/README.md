# PersonalizedVideoMessaging

This is an example repository to show how to integrate Sync.so's LipSync API easily in your workflows. The example shown here is for creating Personalized Video Messages. For voice cloning and TTS, ElevenLabs is used.

## Prerequisites

Before running the code, ensure that you have the following:

- **Sync API key** for lipsyncing.
- **ElevenLabs API key** for TTS & voice cloning.

## Setup and Usage

To get started, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2. **Prepare the CSV file**:

- Fill in the CSV with the required data. Put in the start and end segments in seconds.
- You can specify a `voice_id` in the CSV. If left blank, the code will automatically clone the voice based on the audio from the first entry’s video (which will be used as a reference).

#### Default values:
If you don't specify values for lipsync and TTS options in the CSV, the following default settings will be applied:
- `sync_mode`: `"bounce"`
- `lipsync_model`: `"lipsync-2"`
- `tts_model`: `"eleven_multilingual_v2"`

3. **Update the API keys and CSV path**:

- Open the `constants.py` file and insert your **Sync API key** and **ElevenLabs API key**.
- Set the path to your CSV files in the same configuration file.

4. **Run the application**:

- Execute the main.py script to generate the personalized video messages:
    ```bash
    python main.py
    ```
For more details, refer to the official API documentation for both **Sync API** and **Elevenlabs API**

## Important Notes

- **Audio Requirement**: The video file must contain audio that will be used for voice cloning.

- **Voice Cloning Assumption**: This script assumes that all CSV entries relate to the same person (i.e., voice cloning is done once and used for all entries in the CSV).

- **Language Support**: Refer to the ElevenLabs API docs for supported languages by the model you're using.

- **Temporary File Hosting**: This code uses the temporary file hosting service [Uguu](https://uguu.se/) to generate URLs for TTS audio files. These URLs are then used with the Sync API. By default, the uploaded URLs will be deleted after 3 hours. If you prefer to use your own file hosting service, modify the `upload_file_uguu()` function in `FileProcessor.py` to return a custom URL. The rest of the code should remain unaffected.

- **Job Polling**: Currently, polling for lipsync job completion times out after 60 mins. The code will print all your job_ids in that eventuality. You can also increase/decrease the timeout limit by editing `timeout` arg in `poll_for_status()` function in the `LipSyncService.py`. To fetch output URLs after polling timeout, run the `fetch_updates.py` file which will use the `OUTPUT_CSV_PATH`. 

## Aditional Resources

- [Sync API Documentation](https://docs.sync.so/introduction)
- [ElevenLabs API Documentation](https://elevenlabs.io/docs/api-reference/introduction)


We hope you find this repository useful for integrating personalized video messaging into your workflow! If you have any questions or issues, feel free to open an issue in this repository.
