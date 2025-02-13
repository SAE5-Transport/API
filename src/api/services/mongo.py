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


if __name__ == "__main__":
    print(mongo_user, mongo_password, mongo_host, mongo_port, mongo_db)
    print(health())
