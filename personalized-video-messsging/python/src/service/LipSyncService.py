import os
import requests
from typing import Dict, Optional, Any, List
import time


class LipSyncProcessor():
    """
    Handles lip-syncing using Sync.so API.
    """
    def __init__(self, lipsync_api_key: str):
        self.base_url = "https://api.sync.so/v2/generate"
        
        self.headers = {
            "x-api-key": lipsync_api_key,
            "Content-Type": "application/json"
        }        

    def poll_for_status(self, jobs, timeout=3600, interval=10):
        """
        Poll the API to check the status of submitted lip sync jobs.
        
        This method continuously checks the status of all pending jobs until they
        complete, fail, or the timeout is reached.
        
        Args:
            jobs (list): List of job IDs or tuples (index, job_id) to monitor
            timeout (int, optional): Maximum time in seconds to wait for all jobs.
                                    Defaults to 3600 seconds (60 minutes).
            interval (int, optional): Time in seconds between status checks.
                                     Defaults to 10 seconds.
                                     
        Returns:
            list: Results data for all completed jobs, including their status and
                 output information. Each result includes an 'idx' field matching 
                 the job's original index.
                 
        Raises:
            Exception: If the polling process times out before all jobs complete.
        """
        start_time = time.time()
        results = []
        pending_jobs = set(jobs)
        
        while pending_jobs and (time.time() - start_time < timeout):
            # Check each pending job
            for (i,job_id) in list(pending_jobs):
                try:
                    response = requests.get(f"{self.base_url}/{job_id}", headers=self.headers)
                    response.raise_for_status()

                    data = response.json()
                    data['idx'] = i
                    status = data.get('status')
                    
                    # If job is complete, remove from pending list
                    if status == 'COMPLETED':
                        pending_jobs.remove((i,job_id))
                        results.append(data)
                        print(f"Job {job_id} completed successfully.")
                    elif status in ["FAILED", "REJECTED", "CANCELED", "TIMED_OUT"]:
                        print(f"Lipsync process failed or timed out for {job_id} with status: {status} and error: {data.get('error','')}")
                        pending_jobs.remove((i,job_id))
                        data['outputUrl'] = f'Job Status {status}'
                        results.append(data) 
                except requests.RequestException as e:
                    print(f"Error checking status for job {job_id}: {e}")
            
            # If jobs still pending, wait before next check
            if pending_jobs:
                print(f"Waiting for {len(pending_jobs)} jobs to complete. Next check in {interval} seconds.")
                time.sleep(interval)
        
        # Check for timed out jobs
        if pending_jobs:
            print(f"Polling process timed out waiting for jobs: {pending_jobs}")
            for (i,job_id) in list(pending_jobs):
                data = {'idx':i, 'outputUrl':'POLLING_TIME_OUT'}
                results.append(data)              
        return results

    def process_lip_sync(self, entry:Dict):
        """
        Perform lip-syncing on a video using a specified audio source.
        
        Submits a job to the Sync.so API with video and audio inputs, along with
        configuration options for the lip-syncing process.
        
        Args:
            entry (Dict): Dictionary containing the necessary input data with keys:
                - 'video': URL of the video file to process
                - 'audio': URL of the audio file to use for lip-syncing
                - 'segment_start': Start time (in seconds) of the video segment
                - 'segment_end': End time (in seconds) of the video segment
                
        Returns:
            dict: JSON response from the API containing the job ID and status
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """

        payload = {
                "model": entry['lipsync_model'],
                "input": [
                    {
                        "type": "video",
                        "url": entry['video'],
                        "segments_secs" : [[entry['segment_start'], entry['segment_end']]]
                    },
                    {
                        "type": "audio",
                        "url": entry['audio']
                    }
                ],
                "options": {
                    "pads": [0, 5, 0, 0],
                    "speedup": 1,
                    "output_format": entry['output_format'],
                    "sync_mode": entry['sync_mode'],
                    "active_speaker": True
                }
                # "webhookUrl": "https://your-server.com/webhook"
            }
        
        try:
            response = requests.request(
                method="POST",
                url=self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
        