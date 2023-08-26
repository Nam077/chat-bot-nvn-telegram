from bot.services.user_service import UserService
from bot.utils.db import SessionLocal

db = SessionLocal()
user_service = UserService(db)
print(user_service.get_all_users())