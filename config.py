import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'events_db')
SCRAPER_INTERVAL = int(os.getenv('SCRAPER_INTERVAL', 300))  # 5 minutes
WORKER_INTERVAL = int(os.getenv('WORKER_INTERVAL', 60))     # 1 minute