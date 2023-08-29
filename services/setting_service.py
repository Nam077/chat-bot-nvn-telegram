from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from typing import Optional, Type

from models.models import Setting


class SettingService:
    def __init__(self, db: Session):
        self.db = db

    def create_setting(self, key: str, value: str = '') -> Setting:
        try:
            new_setting = Setting(key=key, value=value)
            self.db.add(new_setting)
            self.db.commit()
            self.db.refresh(new_setting)
            return new_setting
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Key already exists.")

    def get_all_settings(self) -> list[Type[Setting]]:
        return self.db.query(Setting).all()

    def get_setting_by_id(self, setting_id: int) -> Optional[Setting]:
        try:
            return self.db.query(Setting).filter_by(id=setting_id).first()
        except NoResultFound:
            return None

    def get_setting_by_key(self, key: str) -> Setting | Type[Setting] | None:
        try:
            setting = self.db.query(Setting).filter_by(key=key).first()

            if setting is None:
                create_setting = self.create_setting(key=key)
                return create_setting
            else:
                return setting
        except NoResultFound:
            return None

    def get_setting_by_value_bool(self, key: str) -> bool:
        try:
            setting = self.db.query(Setting).filter_by(key=key).first()
            print(setting)
            if setting is None:
                create_setting = self.create_setting(key=key, value='False')
                return create_setting.value == 'True'
            else:
                return setting.value == 'True'
        except NoResultFound:
            return False

    def update_setting(self, setting_id: int, new_key: str, new_value: str) -> Setting:
        setting = self.get_setting_by_id(setting_id)
        if setting:
            setting.key = new_key
            setting.value = new_value
            self.db.commit()
            self.db.refresh(setting)
            return setting
        raise ValueError("Setting not found.")

    def delete_setting(self, setting_id: int) -> bool:
        setting = self.get_setting_by_id(setting_id)
        if setting:
            self.db.delete(setting)
            self.db.commit()
            return True
        return False

    def delete_all_settings(self) -> None:
        self.db.query(Setting).delete()
        self.db.commit()
