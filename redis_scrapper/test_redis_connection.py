import redis
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('redis_test')
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import REDIS_HOST, REDIS_PORT

def test_redis_connection():
    
    # REDIS_HOST = os.getenv('REDIS_HOST', '172.31.160.1')
    # REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    try:
        # Initialize Redis client
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
        
        # Test connection with a PING command
        response = redis_client.ping()
        if response:
            logger.info(f"✅ Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
            
            # Optional: Test set/get operations
            redis_client.set('test_key', 'test_value')
            value = redis_client.get('test_key')
            logger.info(f"Test key-value operation successful: {value}")
            
            # Clean up test key
            redis_client.delete('test_key')
            
    except redis.ConnectionError as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
    except Exception as e:
        logger.error(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    test_redis_connection()