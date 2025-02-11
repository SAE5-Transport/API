'''
    CONFIG
'''
import os

# APP
app_host = os.environ.get('APP_HOST', 'localhost')
app_port = os.environ.get('APP_PORT', '5000')

# POSTRESQL
postgres_user = os.environ.get('POSTGRES_USER')
postgres_password = os.environ.get('POSTGRES_PASSWORD')
postgres_db = os.environ.get('POSTGRES_DB')
postgres_host = os.environ.get('POSTGRES_HOST')
postgres_port = os.environ.get('POSTGRES_PORT')

# MONGODB
mongo_user = os.environ.get('MONGO_USER')
mongo_password = os.environ.get('MONGO_PASSWORD')
mongo_host = os.environ.get('MONGO_HOST')
mongo_port = os.environ.get('MONGO_PORT')
