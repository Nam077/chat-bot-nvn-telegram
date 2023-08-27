from services.key_service import KeyService
from utils.db import SessionLocal

db = SessionLocal()
key_sv = KeyService(db)
keys = key_sv.get_all_keys()
for key in keys:
    print(key)
