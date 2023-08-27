from dotenv import load_dotenv
import os

load_dotenv()

# Bot token
DATABASE_TYPE = os.getenv('DATABASE_TYPE')
DATABASE_NAME = os.getenv('DATABASE_NAME')
FANPAGE_FACEBOOK_URL = os.getenv('FANPAGE_FACEBOOK_URL')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')
DATABASE_NAME_2 = os.getenv('DATABASE_NAME_2')

