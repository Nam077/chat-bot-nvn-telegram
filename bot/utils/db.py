from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.configs.config import DATABASE_URL

# Create a database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
