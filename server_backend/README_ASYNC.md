# Asynchronous Processing for Analytics Data

## Overview
This implementation addresses the timeout issues encountered when processing large ZIP datasets containing extensive mouse movement and keyboard data. The solution implements asynchronous processing to handle these computationally intensive tasks without blocking the main application thread.

## Implementation Architecture

The system utilizes Redis Queue (RQ) for background task processing:
1. Client requests ZIP data analytics through the API
2. Server enqueues the processing job and immediately returns a job ID
3. Client polls for job status using the provided ID
4. Upon completion, results are returned to the client

## Setup Requirements

### Redis Installation

Redis server is required for the task queue functionality:

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS (via Homebrew)
brew install redis
```

Ensure Redis is running:
```bash
redis-server
```

### Required Python Packages

Two additional packages have been added to requirements.txt:
- redis
- rq

Install using:
```bash
pip install -r requirements.txt
```

## Configuration Settings

The following environment variables can be configured in your .env file:

```
# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Optional - leave blank for local development
```

## Worker Process

The background worker must be running to process queued jobs:

```bash
# From the server_backend directory
python worker.py
```

This process should run alongside the Flask application server.

## API Modifications

### New Endpoints
- `/api/analytics/jobs/<job_id>`: Check job status
- `/api/analytics/queue-status`: View task queue information

### Modified Endpoints
- `/api/analytics/<study_id>/zip-data`: Now supports asynchronous operation
  - Parameters:
    - `async=true|false`: Toggle asynchronous processing (defaults to true)
    - `job_id=<id>`: For polling job status
    - Existing parameters remain unchanged

## Frontend Enhancements

The frontend has been updated to:
- Display appropriate loading indicators during async processing
- Implement polling for job completion
- Handle various job states (queued, running, completed, failed)
- Provide better error feedback

## Fallback Mechanism

If Redis is unavailable, the system automatically falls back to synchronous processing, ensuring functionality is maintained, albeit without the performance benefits of async processing.

## Code Organization

- `app/utility/analytics/task_queue.py`: Task queue implementation
- `server_backend/worker.py`: Worker process for job execution
- `app/routes/analytics.py`: Updated API endpoints
- `app/utility/analytics/data_processor.py`: Data processing functions

## Testing the Implementation

To test the asynchronous processing:
1. Start the Redis server
2. Launch the worker process (`python worker.py`)
3. Run the Flask application
4. Access the analytics dashboard in the frontend
5. Monitor the worker console for job processing information

## Troubleshooting

If issues occur:
- Verify the worker process is running
- Check Redis connection status via `/api/analytics/health`
- Examine worker console output for errors
- Review application logs for exceptions