from dotenv import load_dotenv
import os

load_dotenv()

# Bot token
DATABASE_TYPE = os.getenv('DATABASE_TYPE')
DATABASE_NAME = os.getenv('DATABASE_NAME')
FANPAGE_FACEBOOK_URL = os.getenv('FANPAGE_FACEBOOK_URL')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')