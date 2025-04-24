#!/usr/bin/env python
"""
Worker script for processing analytics tasks
Run this in a separate process from the main Flask app
"""
import os
import logging
import redis
from rq import Worker, Queue
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection details
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# Connect to Redis
try:
    logger.info(f"Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}")
    redis_conn = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD
    )
    redis_conn.ping()
    logger.info("Successfully connected to Redis")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {str(e)}")
    raise

# Define the queues to listen to
QUEUES = ['analytics']

if __name__ == '__main__':
    logger.info(f"Starting worker, listening to queues: {', '.join(QUEUES)}")
    # Create queues
    queues = [Queue(name, connection=redis_conn) for name in QUEUES]
    
    # Create and start worker
    worker = Worker(queues, connection=redis_conn)
    logger.info(f"Worker created for queues: {', '.join(QUEUES)}")
    worker.work()