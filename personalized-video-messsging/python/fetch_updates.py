import os
import csv
import json
from urllib.parse import urlparse
from constants import *
from sync import Sync
from sync.core.api_error import ApiError

class FetchOutputs:
    def __init__(self):
        self.client = Sync(api_key=SYNCLABS_API_KEY,)

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
            required_columns = ['video', 'text', 'audio', 'voice_id', 'lipsync_jobID', 'output_url']
            if not all(col in reader.fieldnames for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            for row in reader:
                entry = {
                    'video': row['video'],
                    'text': row['text'],
                    'voice_id': row.get('voice_id'),
                    'audio': row.get('audio'),
                    'lipsync_jobID': row.get('lipsync_jobID'),
                    'outputUrl': row.get('output_url'),
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
        fieldnames = ['video', 'text', 'audio', 'voice_id', 'lipsync_jobID', 'output_url']
        
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

        # load the output csv
        entries = self.load_csv_data(OUTPUT_CSV_PATH)

        # check if outputUrl field is a URL and if not then append to jobs for polling
        jobs = []
        for i, entry in enumerate(entries):
            if bool(urlparse(entry['output_url']).scheme and urlparse(entry['output_url']).netloc):
                continue
            else:
                jobs.append((i,entry['lipsync_jobID']))
        
        for (i,job) in jobs:
            data = self.get_update(job)
            if data:
                if data['status'] == 'COMPLETED':
                    entries[i]['output_url'] = data['output_url']
                else:
                    entries[i]['output_url'] = data['status']
        
        # write the fetched update in output csv
        self.write_dicts_to_csv(entries, OUTPUT_CSV_PATH)

if __name__ == "__main__":

    fetcher = FetchOutputs()
    fetcher.run()
         