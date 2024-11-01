import requests
import json
import redis
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
logger = logging.getLogger('scraper')

class GithubEventsScraper:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
        logger.info(f"Initialized scraper with Redis connection: {REDIS_HOST}:{REDIS_PORT}")

    def scrape_events(self):
        """
        Scrapes public GitHub events.
        Returns list of processed events.
        """
        url = "https://api.github.com/events"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            events = response.json()
            
            # parsing the events to be stored in redis
            processed_events = []
            for event in events:
                processed_events.append({
                    'id': event['id'],
                    'type': event['type'],
                    'actor': event['actor']['login'],
                    'repo': event['repo']['name'],
                    'created_at': event['created_at']
                })
            logger.info(f"Successfully scraped {len(processed_events)} events")
            return processed_events
        except Exception as e:
            logger.error(f"Error scraping GitHub events: {e}")
            return []

    # writing the events to redis cache
    def cache_events(self, events):
        """
        Stores events in Redis with TTL.
        """
        for event in events:
            try:
                key = f"github_event:{event['id']}"
                self.redis_client.setex(
                    key,
                    3600,  # 1 hour TTL
                    json.dumps(event)
                )
                logger.debug(f"Cached event {event['id']}")
            except Exception as e:
                logger.error(f"Error caching event {event['id']}: {e}")

    def run(self):
        """
        Main scraper loop
        """
        logger.info("Starting scraper service")
        while True:
            try:
                events = self.scrape_events()
                self.cache_events(events)
                logger.info(f"Sleeping for {SCRAPER_INTERVAL} seconds")
                time.sleep(SCRAPER_INTERVAL)
            except Exception as e:
                logger.error(f"Error in scraper main loop: {e}")
                time.sleep(60)  # Sleep for a minute on error

if __name__ == "__main__":
    scraper = GithubEventsScraper()
    scraper.run()
