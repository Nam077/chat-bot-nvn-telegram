from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Type
from enum import Enum
from sqlalchemy.orm.exc import NoResultFound

from bot.models.models import Image


class ImageService:
    def __init__(self, db: Session):
        self.db = db

    def create_image(self, url: str) -> Image:
        try:
            new_image = Image(url=url)
            self.db.add(new_image)
            self.db.commit()
            self.db.refresh(new_image)
            return new_image
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Image URL already exists.")

    def get_all_images(self) -> list[Type[Image]]:
        return self.db.query(Image).all()

    def get_image_by_id(self, image_id: int) -> Optional[Image]:
        try:
            return self.db.query(Image).filter_by(id=image_id).first()
        except NoResultFound:
            return None

    def update_image(self, image_id: int, new_url: str) -> Image:
        image = self.get_image_by_id(image_id)
        if image:
            image.url = new_url
            self.db.commit()
            self.db.refresh(image)
            return image
        raise ValueError("Image not found.")

    def delete_image(self, image_id: int) -> bool:
        image = self.get_image_by_id(image_id)
        if image:
            self.db.delete(image)
            self.db.commit()
            return True
        return False

    def delete_all_images(self) -> None:
        self.db.query(Image).delete()
        self.db.commit()

    def create_multiple_images(self, image_urls: List[str]) -> List[Image]:
        self.delete_all_images()
        new_images = [Image(url=image_url) for image_url in image_urls]
        self.db.bulk_save_objects(new_images, return_defaults=True)
        self.db.commit()
        return new_images
