from dotenv import load_dotenv
import os

load_dotenv()

# Bot token
TOKEN = os.getenv('TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
