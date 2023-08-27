from slugify import slugify
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from sqlalchemy.orm.exc import NoResultFound

from bot.models.models import Tag


class TagService:
    def __init__(self, db: Session):
        self.db = db

    def create_tag(self, name: str) -> Tag:
        try:
            new_tag = Tag(name=name)
            self.db.add(new_tag)
            self.db.commit()
            self.db.refresh(new_tag)
            return new_tag
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Tag name already exists.")

    def get_all_tags(self) -> List[Tag]:
        return self.db.query(Tag).all()

    def get_tag_by_id(self, tag_id: int) -> Optional[Tag]:
        try:
            return self.db.query(Tag).filter_by(id=tag_id).first()
        except NoResultFound:
            return None

    def update_tag(self, tag_id: int, new_name: str) -> Tag:
        tag = self.get_tag_by_id(tag_id)
        if tag:
            tag.name = new_name
            self.db.commit()
            self.db.refresh(tag)
            return tag
        raise ValueError("Tag not found.")

    def delete_tag(self, tag_id: int) -> bool:
        tag = self.get_tag_by_id(tag_id)
        if tag:
            self.db.delete(tag)
            self.db.commit()
            return True
        return False

    def delete_all_tags(self) -> None:
        self.db.query(Tag).delete()
        self.db.commit()

    def create_multiple_tags(self, tag_names: List[str]) -> List[Tag]:
        self.delete_all_tags()
        new_tags = [Tag(name=tag_name, slug=slugify(tag_name)) for tag_name in tag_names]
        self.db.bulk_save_objects(new_tags, return_defaults=True)
        self.db.commit()
        return new_tags
