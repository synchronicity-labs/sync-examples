import json
from sync import Sync
from sync.core.api_error import ApiError
from urllib.parse import urlparse
from args import Args

class FetchOutputs:
    def __init__(self):
        
        self.args = Args()
        self.client = Sync(api_key=self.args.SYNCLABS_API_KEY,)

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
            response = self.client.generations.get(
                id=job_id,
            )
            data = json.loads(response.json())
            return data
        except ApiError as e:
            print(f"Error checking status for job {job_id}: {e.status_code} {e.body}")
        return None

    def run(self):

        # load the output json
        with open(self.args.output_json_path, 'r') as file:
            # Load JSON content into a Python dictionary
            entry = json.load(file)

        # check if outputUrl field is a URL and if not then append to jobs for polling
        jobs = []
        if bool(urlparse(entry['output_url']).scheme and urlparse(entry['output_url']).netloc):
            print('outputUrl field already has a URL')
        else:
            jobs.append(entry['lipsync_jobID'])
        
        for job in jobs:
            data = self.get_update(job)
            if data:
                if data['status'] == 'COMPLETED':
                    entry['output_url'] = data['output_url']
                else:
                    entry['output_url'] = data['status']
        
        # write the fetched update in output json
        with open(self.args.output_json_path, 'w') as f:
            json.dump(entry, f, indent=4)

if __name__ == "__main__":

    fetcher = FetchOutputs()
    fetcher.run()
         