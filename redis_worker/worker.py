import mysql.connector
import redis
import json
import time
from datetime import datetime
import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import *


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('worker')

class DatabaseWorker:
    def __init__(self):
        self.connect_mysql()
        self.connect_redis()
        self.create_table()
        logger.info("Worker initialized successfully")

    def connect_mysql(self):
        """
        Establishes MySQL connection with retry logic
        """
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.mysql_conn = mysql.connector.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DATABASE
                )
                self.cursor = self.mysql_conn.cursor()
                logger.info("Successfully connected to MySQL")
                return
            except Exception as e:
                retry_count += 1
                logger.error(f"Failed to connect to MySQL (attempt {retry_count}/{max_retries}): {e}")
                time.sleep(5)
        
        raise Exception("Failed to connect to MySQL after maximum retries")

    def connect_redis(self):
        """
        Establishes Redis connection with retry logic
        """
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.redis_client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    decode_responses=True
                )
                self.redis_client.ping()  # Test connection
                logger.info("Successfully connected to Redis")
                return
            except Exception as e:
                retry_count += 1
                logger.error(f"Failed to connect to Redis (attempt {retry_count}/{max_retries}): {e}")
                time.sleep(5)
        
        raise Exception("Failed to connect to Redis after maximum retries")

    def create_table(self):
        """
        Creates events table if it doesn't exist
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS github_events (
            id VARCHAR(255) PRIMARY KEY,
            event_type VARCHAR(255),
            actor VARCHAR(255),
            repo VARCHAR(255),
            created_at DATETIME,
            processed_at DATETIME,
            INDEX idx_created_at (created_at)
        )
        """
        self.cursor.execute(create_table_query)
        self.mysql_conn.commit()
        logger.info("Ensured github_events table exists")

    def process_events(self):
        """
        Processes events from Redis cache and stores them in MySQL
        """
        try:
            pattern = "github_event:*"
            event_keys = self.redis_client.keys(pattern)
            
            if not event_keys:
                logger.debug("No events found to process")
                return

            logger.info(f"Found {len(event_keys)} events to process")
            
            for key in event_keys:
                try:
                    # Get and parse event data
                    event_data = self.redis_client.get(key)
                    if not event_data:
                        continue
                        
                    event = json.loads(event_data)
                    
                    # Convert ISO 8601 datetime to MySQL format
                    created_at = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Insert into MySQL
                    insert_query = """
                    INSERT INTO github_events 
                    (id, event_type, actor, repo, created_at, processed_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    processed_at = VALUES(processed_at)
                    """
                    
                    values = (
                        event['id'],
                        event['type'],
                        event['actor'],
                        event['repo'],
                        created_at,  # Use the converted datetime
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    self.cursor.execute(insert_query, values)
                    self.mysql_conn.commit()
                    
                    # Delete processed event from Redis
                    self.redis_client.delete(key)
                    logger.debug(f"Successfully processed and deleted event {key}")
                    
                except Exception as e:
                    logger.error(f"Error processing event {key}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in process_events: {e}")
            # Attempt to reconnect
            self.connect_mysql()
            self.connect_redis()

    def run(self):
        """
        Main worker loop
        """
        logger.info("Starting worker service")
        while True:
            try:
                self.process_events()
                logger.info(f"Sleeping for {WORKER_INTERVAL} seconds")
                time.sleep(WORKER_INTERVAL)
            except Exception as e:
                logger.error(f"Error in worker main loop: {e}")
                time.sleep(60)  # Sleep for a minute on error

if __name__ == "__main__":
    worker = DatabaseWorker()
    worker.run()