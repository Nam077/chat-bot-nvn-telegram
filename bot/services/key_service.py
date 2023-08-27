from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Type
from sqlalchemy.orm.exc import NoResultFound

from bot.models.models import Key


class KeyService:
    def __init__(self, db: Session):
        self.db = db

    def create_key(self, key_value: str) -> Key:
        try:
            new_key = Key(key=key_value)
            self.db.add(new_key)
            self.db.commit()
            self.db.refresh(new_key)
            return new_key
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Key already exists.")

    def get_all_keys(self) -> list[Type[Key]]:
        return self.db.query(Key).all()

    def get_key_by_id(self, key_id: int) -> Optional[Key]:
        try:
            return self.db.query(Key).filter_by(id=key_id).first()
        except NoResultFound:
            return None

    def update_key(self, key_id: int, new_key_value: str) -> Key:
        key = self.get_key_by_id(key_id)
        if key:
            key.key = new_key_value
            self.db.commit()
            self.db.refresh(key)
            return key
        raise ValueError("Key not found.")

    def delete_key(self, key_id: int) -> bool:
        key = self.get_key_by_id(key_id)
        if key:
            self.db.delete(key)
            self.db.commit()
            return True
        return False

    def delete_all_keys(self) -> None:
        self.db.query(Key).delete()
        self.db.commit()

    def create_multiple_keys(self, key_values: List[str]) -> List[Key]:
        new_keys = [Key(key=key_value) for key_value in key_values]
        self.db.bulk_save_objects(new_keys)
        self.db.commit()
        return new_keys

    def get_key_by_value(self, key_value: str) -> Optional[Key]:
        return self.db.query(Key).filter_by(key=key_value.lower()).first()
