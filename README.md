# redis_app

A simple redis application that scraps github public events and writes into redis. A worker which reads redis and writes into mysql 

## How to run

* Need to install python dependencies. Create virtual environment and install dependencies.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

* Run docker images for mysql and redis.

Running docker image for redis cache listening on port 6379
```
docker run -d --name redis-cache -p 6379:6379 redis:latest
```

Running docker mysql image running on port 3306.

```
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=your_password -e MYSQL_DATABASE=your_database 
-e MYSQL_USER=your_user -e MYSQL_PASSWORD=your_user_password -p 3306:3306 -v mysql_data:/var/lib/mysql -d mysql:latest
```

* Update the config.py file with the correct mysql and redis credentials.

* Run the scrapper.py file to start scraping github public events and writing into redis cache.

```
python scrapper.py
```

* Ensure the events_db database is created in mysql.

* Run the worker.py file to read events from redis and write into mysql.

```
python worker.py
```

### todo:

* Add unit tests
* Add logging
* Fix docker compose file
* Fix dockerfile.scrapper
* Fix dockerfile.worker

### Notes for windows and wsl2 users:

If you are using windows to run docker and running python code in WSL2, you need to update the config.py file with the correct redis and mysql host.

```
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
```

Instead of localhost, you need to use the ip address of the docker container. You can get the ip address of the docker container by running the following command.

Inside WSL2
```
route -n (to get the ip address of the WSL gateway that will be used as the redis and mysql host for accessing docker containers on windows)
```
