'''
    MongoDB connection
'''
import pymongo
from api.utils.config import mongo_user, mongo_password, mongo_host, mongo_port, mongo_db


def connector():
    '''
        Get conn
    '''
    return pymongo.MongoClient(
        f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}?authSource=admin")


def health():
    '''
        Check health of the connection
    '''
    try:
        conn = connector()
        conn.server_info()
        conn.close()
        return True
    except Exception as error:
        print(error)
        return False


def save(data, collection_name):
    '''
        Save data to MongoDB
    '''
    try:
        conn = connector()
        db = conn[mongo_db]
        collection = db[collection_name]
        collection.insert_one(data)
        conn.close()
        return True
    except Exception as error:
        print(error)
        return False


def save_json(json_file, collection_name):
    '''
        Save JSON file to MongoDB
    '''
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            return save(data, collection_name)
    except Exception as error:
        print(error)
        return False


def get_all(collection_name):
    '''
        Get all data from MongoDB
    '''
    try:
        conn = connector()
        db = conn[mongo_db]
        collection = db[collection_name]
        data = list(collection.find())
        conn.close()
        return data
    except Exception as error:
        print(error)
        return None


def get_one(collection_name, filter_to_use):
    '''
        Get one data from MongoDB
    '''
    try:
        conn = connector()
        db = conn[mongo_db]
        collection = db[collection_name]
        data = collection.find_one(filter_to_use)
        conn.close()
        return data
    except Exception as error:
        print(error)
        return None


def delete(collection_name, filter_to_use):
    '''
        Delete data from MongoDB
    '''
    try:
        conn = connector()
        db = conn[mongo_db]
        collection = db[collection_name]
        collection.delete_one(filter_to_use)
        conn.close()
        return True
    except Exception as error:
        print(error)
        return False
