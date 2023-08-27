from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.configs.config import DATABASE_NAME, DATABASE_TYPE, DATABASE_NAME_2
import os

db_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'database')

if not os.path.exists(db_folder):
    os.makedirs(db_folder)

db_file = os.path.join(db_folder, DATABASE_NAME)
db_file_2 = os.path.join(db_folder, DATABASE_NAME_2)

try:
    engine = create_engine(f'{DATABASE_TYPE}:///{db_file}', connect_args={'check_same_thread': False})
    engine_2 = create_engine(f'{DATABASE_TYPE}:///{db_file_2}', connect_args={'check_same_thread': False})
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    SessionLocal_2 = sessionmaker(bind=engine_2, autocommit=False, autoflush=False)
    print('Connected to database')
except Exception as e:
    print(e)
    print('Cannot connect to database')
    exit(1)
