from sqlalchemy import Column, Integer, String

from bot.models import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String)

    def __init__(self, username: str, full_name: str):
        self.username = username
        self.full_name = full_name

    def __str__(self):
        return f'User(id={self.id}, username={self.username}, full_name={self.full_name})'
