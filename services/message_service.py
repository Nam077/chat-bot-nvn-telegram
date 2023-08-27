from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from sqlalchemy.orm.exc import NoResultFound

from models.models import Message


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, value: str) -> Message:
        try:
            new_message = Message(value=value)
            self.db.add(new_message)
            self.db.commit()
            self.db.refresh(new_message)
            return new_message
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Message value already exists.")

    def get_all_messages(self) -> List[Message]:
        return self.db.query(Message).all()

    def get_message_by_id(self, message_id: int) -> Optional[Message]:
        try:
            return self.db.query(Message).filter_by(id=message_id).first()
        except NoResultFound:
            return None

    def update_message(self, message_id: int, new_value: str) -> Message:
        message = self.get_message_by_id(message_id)
        if message:
            message.value = new_value
            self.db.commit()
            self.db.refresh(message)
            return message
        raise ValueError("Message not found.")

    def delete_message(self, message_id: int) -> bool:
        message = self.get_message_by_id(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False

    def delete_all_messages(self) -> None:
        self.db.query(Message).delete()
        self.db.commit()

    def create_multiple_messages(self, message_values: List[str]) -> List[Message]:
        self.delete_all_messages()
        new_messages = [Message(value=message_value) for message_value in message_values]
        self.db.bulk_save_objects(new_messages, return_defaults=True)
        self.db.commit()
        return new_messages
