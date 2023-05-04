from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)


cluster = os.getenv('MONGO_CLUSTER')
user = os.getenv('MONGO_USER')
password = os.getenv('MONGO_PASSWORD')
identifier = os.getenv('MONGO_IDENTIFIER')


def get_db():
    print(cluster)
    return connect_db().get_database(cluster)


def connect_db():
    client = MongoClient(
        'mongodb+srv://' + user + ':' + password + '@' + identifier + '.mongodb.net/?retryWrites=true&w=majority')
    return client
