from datetime import datetime
from pymongo import MongoClient
import os

mongo_01_ip = 'nosql-router-01'
mongo_02_ip = 'nosql-router-02'
mongo_port1 = 27017
mongo_port2 = 27017
mongo_database = os.getenv('DATABASE_NAME')
mongo_user = os.getenv('ROOT_USERNAME')
mongo_password = os.getenv('ROOT_PASSWORD')

def get_db_connection():
    mongo_url = f'mongodb://{mongo_user}:{mongo_password}@{mongo_01_ip}:{mongo_port1},{mongo_02_ip}:{mongo_port2}/{mongo_database}?authSource=admin'
    client = MongoClient(mongo_url)
    return client[mongo_database]

def get_db_client():
    mongo_url = f'mongodb://{mongo_user}:{mongo_password}@{mongo_01_ip}:{mongo_port1},{mongo_02_ip}:{mongo_port2}/{mongo_database}?authSource=admin'
    return MongoClient(mongo_url)
