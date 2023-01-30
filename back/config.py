import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_DB_TEST = os.environ.get('POSTGRES_DB_TEST')
POSTGRES_HOST_TEST = os.environ.get('POSTGRES_HOST_TEST')


REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_DB = os.environ.get('REDIS_DB')
REDIS_DB_TEST = os.environ.get('REDIS_DB_TEST')
REDIS_HOST_TEST = os.environ.get('REDIS_HOST_TEST')
