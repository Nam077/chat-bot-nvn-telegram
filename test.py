from services.key_service import KeyService
from utils.db import SessionLocal

db = SessionLocal()
key_service = KeyService(db)
keys = key_service.get_all_keys()
for key in keys:
    print(key.font)
