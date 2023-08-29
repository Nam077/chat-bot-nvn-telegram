from models.models import Base
from utils.db import engine

Base.metadata.create_all(bind=engine)
