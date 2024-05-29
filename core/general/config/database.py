import os

from core.modules.database.schemes.pool import DatabaseData

database_data = DatabaseData(
    user=os.getenv('DATABASE_USER'),
    password=os.getenv('DATABASE_PASSWORD'),
    host=os.getenv('DATABASE_HOST'),
    name=os.getenv('DATABASE_NAME'),
    port=int(os.getenv('DATABASE_PORT'))
)
