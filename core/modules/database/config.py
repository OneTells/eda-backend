import os


class ConnectionData:
    USER = os.getenv('DATABASE_USER')
    PASSWORD = os.getenv('DATABASE_PASSWORD')
    HOST = os.getenv('DATABASE_HOST')
    NAME = os.getenv('DATABASE_NAME')
    PORT = int(os.getenv('DATABASE_PORT'))

    DSN = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'
