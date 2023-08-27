from typing import List

from slugify import slugify
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

from bot.utils.db import engine, engine_2

Base = declarative_base()
Base_2 = declarative_base()


class EnumTableName(Enum):
    FONTS = "fonts"
    LINKS = "links"
    IMAGES = "images"
    KEYS = "keys"
    MESSAGES = "messages"
    SETTINGS = "settings"
    TAGS = "tags"
    LINK_FONT_ASSOCIATION = "link_font_association"
    IMAGE_FONT_ASSOCIATION = "image_font_association"
    MESSAGE_FONT_ASSOCIATION = "message_font_association"
    FONT_TAG_ASSOCIATION = "font_tag_association"


# Define association
association_table_link_font = Table(
    EnumTableName.LINK_FONT_ASSOCIATION.value, Base.metadata,
    Column('link_id', Integer, ForeignKey(f'{EnumTableName.LINKS.value}.id', ondelete='CASCADE')),
    Column('font_id', Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id', ondelete='CASCADE'))
)

association_table_image_font = Table(
    EnumTableName.IMAGE_FONT_ASSOCIATION.value, Base.metadata,
    Column('image_id', Integer, ForeignKey(f'{EnumTableName.IMAGES.value}.id', ondelete='CASCADE')),
    Column('font_id', Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id', ondelete='CASCADE'))
)

association_table_message_font = Table(
    EnumTableName.MESSAGE_FONT_ASSOCIATION.value, Base.metadata,
    Column('message_id', Integer, ForeignKey(f'{EnumTableName.MESSAGES.value}.id', ondelete='CASCADE')),
    Column('font_id', Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id', ondelete='CASCADE'))
)

association_table_font_tag = Table(
    EnumTableName.FONT_TAG_ASSOCIATION.value, Base.metadata,
    Column('font_id', Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey(f'{EnumTableName.TAGS.value}.id', ondelete='CASCADE'))
)


class Link(Base):
    __tablename__ = EnumTableName.LINKS.value
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(unique=True, nullable=False)
    fonts: Mapped[List["Font"]] = relationship("Font", secondary=association_table_link_font, back_populates="links")

    def __str__(self):
        return f'Link(id={self.id}, url={self.url})'


class Image(Base):
    __tablename__ = EnumTableName.IMAGES.value
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(unique=True, nullable=False)
    fonts: Mapped[List["Font"]] = relationship("Font", secondary=association_table_image_font, back_populates="images")

    def __str__(self):
        return f'Image(id={self.id}, url={self.url})'


class Key(Base):
    __tablename__ = EnumTableName.KEYS.value
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    value: Mapped[str] = mapped_column(nullable=False, default='')
    font_id: Mapped[int] = mapped_column(Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id', ondelete='CASCADE'),
                                         nullable=True)
    font: Mapped["Font"] = relationship("Font", back_populates="keys")

    def __str__(self):
        return f'Key(id={self.id}, name={self.name}, value={self.value})'


class Message(Base):
    __tablename__ = EnumTableName.MESSAGES.value
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(nullable=False)
    fonts: Mapped[List["Font"]] = relationship("Font", secondary=association_table_message_font,
                                               back_populates="messages")

    def __str__(self):
        return f'Message(id={self.id}, value={self.value})'


class Setting(Base):
    __tablename__ = EnumTableName.SETTINGS.value
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True, nullable=False)
    value: Mapped[str] = mapped_column(nullable=False, default='')

    def __str__(self):
        return f'Settings(id={self.id}, key={self.key})'


class Tag(Base):
    __tablename__ = EnumTableName.TAGS.value
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False, default='')
    fonts: Mapped[List["Font"]] = relationship("Font", secondary=association_table_font_tag, back_populates="tags")

    def __str__(self):
        return f'Tag(id={self.id}, name={self.name})'


class Font(Base):
    __tablename__ = EnumTableName.FONTS.value
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    post_link: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[bool] = mapped_column(nullable=False, default=True)
    keys: Mapped[List[Key]] = relationship("Key", back_populates="font")
    links: Mapped[List[Link]] = relationship("Link", secondary=association_table_link_font, back_populates="fonts")
    images: Mapped[List[Image]] = relationship("Image", secondary=association_table_image_font, back_populates="fonts")
    messages: Mapped[List[Message]] = relationship("Message", secondary=association_table_message_font,
                                                   back_populates="fonts")
    tags: Mapped[List[Tag]] = relationship("Tag", secondary=association_table_font_tag, back_populates="fonts")

    def __str__(self):
        return f'Font(id={self.id}, name={self.name}, post_link={self.post_link}, slug={self.slug}, description={self.description}, status={self.status}, keys={self.keys}, links={self.links}, images={self.images}, messages={self.messages}, tags={self.tags})'


class FontGlobal(Base_2):
    __tablename__ = EnumTableName.FONTS.value
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    thumbnail: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    category_name: Mapped[str] = mapped_column(nullable=True)
    download_link: Mapped[str] = mapped_column(nullable=True)
    detail_images: Mapped[str] = mapped_column(nullable=True)
    more_link: Mapped[str] = mapped_column(nullable=True)
    file_name: Mapped[str] = mapped_column(nullable=True)
    link_drive: Mapped[str] = mapped_column(nullable=True)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)

    def __str__(self):
        return f'Font(id={self.id}, name={self.name}, url={self.url}, thumbnail={self.thumbnail}, description={self.description}, category_name={self.category_name}, download_link={self.download_link}, detail_images={self.detail_images}, more_link={self.more_link}, file_name={self.file_name}, link_drive={self.link_drive}, slug={self.slug})'
