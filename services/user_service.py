from sqlalchemy.orm import Session
from models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        return self.db.query(User).filter_by(id=user_id).first()

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter_by(username=username).first()

    def create_user(self, user: User):
        existing_user = self.get_user_by_username(user.username)
        if existing_user:
            raise Exception("Username already exists.")

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, new_user_data: dict):
        db_user = self.db.query(User).filter_by(id=user_id).first()

        if "username" in new_user_data:
            existing_user = self.get_user_by_username(new_user_data["username"])
            if existing_user and existing_user.id != db_user.id:
                raise Exception("Username already exists.")

        for key, value in new_user_data.items():
            setattr(db_user, key, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int):
        db_user = self.db.query(User).filter_by(id=user_id).first()
        self.db.delete(db_user)
        self.db.commit()
        return True

    def get_all_users(self):
        return self.db.query(User).all()
