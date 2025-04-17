import os
import json
import requests
from urllib.parse import urlparse
from args import Args

class FetchOutputs:
    def __init__(self):
        self.base_url = "https://api.sync.so/v2/generate"
        self.args = Args()
        self.headers = {
            "x-api-key": self.args.SYNCLABS_API_KEY,
            "Content-Type": "application/json"
        }

    def get_update(self, job_id):
        """
        Check the status of submitted lip sync job.
        
        Args:
            job_id (str): Job ID to fetch an update for
                            
        Returns:
            dict: json response from checking the status of the job
                 
        Raises:
            Exception: If the request to get an update has an error.
        """
        try:
            response = requests.get(f"{self.base_url}/{job_id}", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"Error checking status for job {job_id}: {e}")
        return None

    def run(self):

        # load the output json
        with open(self.args.output_json_path, 'r') as file:
            # Load JSON content into a Python dictionary
            entry = json.load(file)

        # check if outputUrl field is a URL and if not then append to jobs for polling
        jobs = []
        if bool(urlparse(entry['outputUrl']).scheme and urlparse(entry['outputUrl']).netloc):
            print('outputUrl field already has a URL')
        else:
            jobs.append(entry['lipsync_jobID'])
        
        for job in jobs:
            data = self.get_update(job)
            if data:
                if data['status'] == 'COMPLETED':
                    entry['outputUrl'] = data['outputUrl']
                else:
                    entry['outputUrl'] = data['status']
        
        # write the fetched update in output json
        with open(self.args.output_json_path, 'w') as f:
            json.dump(entry, f, indent=4)

if __name__ == "__main__":

    fetcher = FetchOutputs()
    fetcher.run()
         