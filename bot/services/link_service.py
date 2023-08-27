from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Type
from enum import Enum
from sqlalchemy.orm.exc import NoResultFound

from bot.models.models import Link


class LinkService:
    def __init__(self, db: Session):
        self.db = db

    def create_link(self, url: str) -> Link:
        try:
            new_link = Link(url=url)
            self.db.add(new_link)
            self.db.commit()
            self.db.refresh(new_link)
            return new_link
        except IntegrityError:
            self.db.rollback()
            raise ValueError("URL already exists.")

    def get_all_links(self) -> list[Type[Link]]:
        return self.db.query(Link).all()

    def get_link_by_id(self, link_id: int) -> Optional[Link]:
        try:
            return self.db.query(Link).filter_by(id=link_id).first()
        except NoResultFound:
            return None

    def update_link(self, link_id: int, new_url: str) -> Link:
        link = self.get_link_by_id(link_id)
        if link:
            link.url = new_url
            self.db.commit()
            self.db.refresh(link)
            return link
        raise ValueError("Link not found.")

    def delete_link(self, link_id: int) -> bool:
        link = self.get_link_by_id(link_id)
        if link:
            self.db.delete(link)
            self.db.commit()
            return True
        return False

    def delete_all_links(self) -> None:
        self.db.query(Link).delete()
        self.db.commit()

    def create_multiple_links(self, link_urls: List[str]) -> List[Link]:
        self.delete_all_links()
        new_links = [Link(url=link_url) for link_url in link_urls]
        self.db.bulk_save_objects(new_links, return_defaults=True)
        self.db.commit()
        return new_links
