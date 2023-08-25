from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.configs.config import DATABASE_URL

# Create a database session
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    print('Connected to database')
except Exception as e:
    print(e)
    print('Cannot connect to database')
    exit(1)
