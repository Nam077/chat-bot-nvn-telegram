from dotenv import load_dotenv
import os

load_dotenv()

# Bot token
DATABASE_TYPE = os.getenv('DATABASE_TYPE')
DATABASE_NAME = os.getenv('DATABASE_NAME')
