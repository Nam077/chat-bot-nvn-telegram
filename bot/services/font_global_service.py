from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from enum import Enum
from typing import List, Optional, Type

from bot.models.models import FontGlobal


class FontGlobalService:
    def __init__(self, db: Session):
        self.db = db

    def create_font(self, name: str, url: str, thumbnail: str, description: str = None,
                    category_name: str = None, download_link: str = None,
                    detail_images: str = None, more_link: str = None, file_name: str = None,
                    link_drive: str = None, slug: str = None) -> FontGlobal:
        try:
            new_font = FontGlobal(name=name, url=url, thumbnail=thumbnail, description=description,
                                  category_name=category_name, download_link=download_link,
                                  detail_images=detail_images, more_link=more_link,
                                  file_name=file_name, link_drive=link_drive, slug=slug)
            self.db.add(new_font)
            self.db.commit()
            self.db.refresh(new_font)
            return new_font
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Slug already exists.")

    def get_all_fonts(self) -> list[Type[FontGlobal]]:
        return self.db.query(FontGlobal).all()

    def get_font_by_id(self, font_id: int) -> Optional[FontGlobal]:
        try:
            return self.db.query(FontGlobal).filter_by(id=font_id).first()
        except NoResultFound:
            return None

    def get_font_by_slug(self, slug: str) -> Optional[FontGlobal]:
        try:
            return self.db.query(FontGlobal).filter_by(slug=slug).first()
        except NoResultFound:
            return None

    def update_font(self, font_id: int, new_data: dict) -> FontGlobal:
        font = self.get_font_by_id(font_id)
        if font:
            for key, value in new_data.items():
                setattr(font, key, value)
            self.db.commit()
            self.db.refresh(font)
            return font
        raise ValueError("Font not found.")

    def delete_font(self, font_id: int) -> bool:
        font = self.get_font_by_id(font_id)
        if font:
            self.db.delete(font)
            self.db.commit()
            return True
        return False

    def delete_all_fonts(self) -> None:
        self.db.query(FontGlobal).delete()
        self.db.commit()

    def get_random_font_by_name(self, name='', limit=10) -> list[Type[FontGlobal]]:
        query = self.db.query(FontGlobal)
        if name:
            query = query.filter(FontGlobal.name.ilike(f'%{name}%'))
        return query.order_by(FontGlobal.id.desc()).limit(limit).all()
