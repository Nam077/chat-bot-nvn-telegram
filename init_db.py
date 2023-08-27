from bot.utils.db import engine
from bot.models import Base
from bot.models.models import *

Base.metadata.create_all(bind=engine)
