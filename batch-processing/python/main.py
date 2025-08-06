import time
import requests
import argparse
from sync import Sync

sync = Sync(api_key="<YOUR_API_KEY>")

def create_batch(input_file, dry_run=False):
    batch_response = sync.batch.create(
        input=open(input_file, "rb"),
        webhook_url="<YOUR_WEBHOOK_URL>",
        dry_run=dry_run
    )
    if dry_run:
        print(f"Dry run validation successful for file: {input_file}")
        return None
    return batch_response.id


def poll_batch_job(batch_id):
    """Poll the batch job status until completion"""
    batch_response = sync.batch.get(batch_id)
    batch_status = batch_response.status
    while True:
        if batch_status == "COMPLETED" or batch_status == "FAILED":
            break
        batch_response = sync.batch.get(batch_id)
        batch_status = batch_response.status
        time.sleep(60)
    output_url = batch_response.output_url
    if output_url:
        output_path = 'output.jsonl'
        response = requests.get(output_url)
        with open(output_path, 'wb') as f:
            f.write(response.content)
    
    if batch_status == "COMPLETED":
        print(f"Batch job {batch_id} completed! Result saved to {output_path}")
    else:
        print(f"Batch job {batch_id} failed. Result saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create and optionally monitor batch processing jobs")
    parser.add_argument("--input-file", help="Path to the input JSONL file for batch processing")
    parser.add_argument("--monitor", action="store_true", default=False, help="Poll for batch status until completion (default: False)")
    parser.add_argument("--batch-id", help="Existing batch ID to monitor (requires --monitor flag)")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Validate input file without processing (default: False)")
    
    args = parser.parse_args()
    
    # Validation logic
    if args.batch_id:
        if not args.monitor:
            parser.error("--batch-id requires --monitor flag to be specified")
        if args.dry_run:
            parser.error("--dry-run cannot be used with --batch-id")
    else:
        if not args.input_file:
            parser.error("--input-file is required when not using --batch-id")
    
    if args.batch_id:
        # Use existing batch ID for monitoring
        batch_id = args.batch_id
        print(f"Monitoring existing batch with ID: {batch_id}")
        poll_batch_job(batch_id)
    else:
        # Create new batch or validate
        batch_id = create_batch(args.input_file, dry_run=args.dry_run)
        
        if args.dry_run:
            # Dry run mode - just validation, no monitoring
            print("Validation complete. No batch was created.")
        else:
            # Normal mode - conditionally monitor the new batch
            if args.monitor:
                poll_batch_job(batch_id)
            else:
                print(f"Batch {batch_id} created. Run `python main.py --batch-id {batch_id} --monitor` to monitor the batch progress")
