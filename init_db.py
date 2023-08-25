from bot.utils.db import engine
from bot.models import Base
from bot.models.user import User

Base.metadata.create_all(bind=engine)
