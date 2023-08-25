from bot.utils.db import engine
from bot.models import Base

Base.metadata.create_all(bind=engine)
