from bot.services.key_service import KeyService
from bot.utils.db import SessionLocal

db = SessionLocal()
key_sv = KeyService(db)
print(key_sv.get_all_keys())