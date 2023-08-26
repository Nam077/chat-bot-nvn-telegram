from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.configs.config import DATABASE_NAME, DATABASE_TYPE
import os

db_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'database')

if not os.path.exists(db_folder):
    os.makedirs(db_folder)

db_file = os.path.join(db_folder, DATABASE_NAME)

try:
    engine = create_engine(f'{DATABASE_TYPE}:///{db_file}', connect_args={'check_same_thread': False})
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

except Exception as e:
    print(e)
    print('Cannot connect to database')
    exit(1)
