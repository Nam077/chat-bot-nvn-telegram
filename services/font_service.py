from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Type, Dict
from sqlalchemy.orm.exc import NoResultFound

from models.models import Key, Link, Image, Font, Tag, Message


class FontService:
    def __init__(self, db: Session):
        self.db = db

    def create_font(self, name: str, post_link: str, description: str, status: bool = True,
                    keys: List[Key] = None, links: List[Link] = None, images: List[Image] = None,
                    messages: List[Message] = None, tags: List[Tag] = None) -> Font:
        try:
            new_font = Font(name=name, post_link=post_link, description=description,
                            status=status)

            if keys:
                new_font.keys = keys
            if links:
                new_font.links = links
            if images:
                new_font.images = images
            if messages:
                new_font.messages = messages
            if tags:
                new_font.tags = tags

            self.db.add(new_font)
            self.db.commit()
            self.db.refresh(new_font)
            return new_font
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Font name or slug already exists.")

    def create_multiple_fonts(self, font_data_list: List[Dict]) -> List[Font]:
        self.delete_all_fonts()  # Assuming you have a method to delete all fonts
        fonts_to_create = []
        for font_data in font_data_list:
            name = font_data.get('name')
            slug = font_data.get('slug')
            post_link = font_data.get('post_link')
            description = font_data.get('description')
            status = font_data.get('status', True)
            font = Font(name=name, slug=slug, post_link=post_link, description=description, status=status)
            font.keys = font_data.get('keys', [])
            font.links = font_data.get('links', [])
            font.images = font_data.get('images', [])
            font.messages = font_data.get('messages', [])
            font.tags = font_data.get('tags', [])
            fonts_to_create.append(font)
        self.db.add_all(fonts_to_create)
        self.db.flush()
        self.db.commit()
        return fonts_to_create

    def get_all_fonts(self) -> list[Type[Font]]:
        return self.db.query(Font).all()

    def get_font_by_id(self, font_id: int) -> Optional[Font]:
        try:
            return self.db.query(Font).filter_by(id=font_id).first()
        except NoResultFound:
            return None

    def update_font(self, font_id: int, name: str, thumbnail: str, post_link: str, slug: str, description: str,
                    status: bool) -> Font:
        font = self.get_font_by_id(font_id)
        if font:
            font.name = name
            font.thumbnail = thumbnail
            font.post_link = post_link
            font.slug = slug
            font.description = description
            font.status = status
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
        self.db.query(Font).delete()
        self.db.commit()
