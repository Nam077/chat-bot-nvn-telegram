# bot/service/user_service.py

from sqlalchemy.orm import Session
from bot.models.user import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, new_user_data: dict):
        db_user = self.db.query(User).filter(User.id == user_id).first()
        for key, value in new_user_data.items():
            setattr(db_user, key, value)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int):
        db_user = self.db.query(User).filter(User.id == user_id).first()
        self.db.delete(db_user)
        self.db.commit()
