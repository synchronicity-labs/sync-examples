# Sync Batch Processing Script

Process multiple lipsync generation requests efficiently using the [Sync Batch API](https://docs.sync.so/api-reference/guides/batch-processing).

## Prerequisites

- **Python 3.8+**
- **Sync Scale or Enterprise plan** - Batch API is not available on lower-tier plans
- **Valid API Key** from your Sync account

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API credentials in `main.py`:**
   ```python
   sync = Sync(api_key="your-actual-api-key-here")
   ```

3. **Optional webhook URL** for completion notifications:
   ```python
   webhook_url="https://your-webhook-endpoint.com/batch-complete"
   ```

## Usage

### Create and monitor a new batch:
```bash
python main.py --input-file input.jsonl --monitor
```

### Create batch without monitoring:
```bash
python main.py --input-file input.jsonl
```

### Validate input file without processing:
```bash
python main.py --input-file input.jsonl --dry-run
```

### Monitor existing batch:
```bash
python main.py --batch-id your_batch_id --monitor
```

## Input File Format

Your input file must be in [JSON Lines format](https://docs.sync.so/api-reference/guides/batch-processing#input-format) (.jsonl):

```jsonl
{"request_id": "video_001", "endpoint": "/v2/generate", "payload": {"model": "lipsync-2", "input": [{"type": "video", "url": "https://example.com/video1.mp4"}, {"type": "audio", "url": "https://example.com/audio1.wav"}]}}
{"request_id": "video_002", "endpoint": "/v2/generate", "payload": {"model": "lipsync-2", "input": [{"type": "video", "url": "https://example.com/video2.mp4"}, {"type": "audio", "url": "https://example.com/audio2.wav"}]}}
```

### Required fields per line:
- `request_id`: Unique identifier for each request
- `endpoint`: Must be `"/v2/generate"`
- `payload`: [Standard generation request payload](https://docs.sync.so/api-reference/api/generate-api/create)

## Important Limits

- **Max file size**: 5MB
- **Max requests per batch**: 1000
- **Plan requirement**: Scale or Enterprise (you'll get a 402 error on lower plans)

## Key Features

- **Results downloaded to local `output.jsonl`**
- **Dry run validation**: Test input files without creating batches using `--dry-run`
- **Status monitoring**: Polls every 60 seconds when `--monitor` is used
- **Validation**: Prevents no-op commands (e.g., batch-id without monitor flag)
- **Webhook support**: Optional real-time notifications

## Documentation

- [Batch API Reference](https://docs.sync.so/api-reference/guides/batch-processing)
- [Sync API Documentation](https://docs.sync.so/api-reference)
