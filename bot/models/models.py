from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from bot.models import Base


class EnumTableName(Enum):
    FONTS = "fonts"
    LINKS = "links"
    IMAGES = "images"
    KEYS = "keys"
    MESSAGES = "messages"
    LINK_FONT_ASSOCIATION = "link_font_association"
    IMAGE_FONT_ASSOCIATION = "image_font_association"
    MESSAGE_FONT_ASSOCIATION = "message_font_association"


link_font_association = Table(EnumTableName.LINK_FONT_ASSOCIATION.value, Base.metadata,
                              Column('font_id', Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id')),
                              Column('link_id', Integer, ForeignKey(f'{EnumTableName.LINKS.value}.id'))
                              )

image_font_association = Table(EnumTableName.IMAGE_FONT_ASSOCIATION.value, Base.metadata,
                               Column('font_id', Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id')),
                               Column('image_id', Integer, ForeignKey(f'{EnumTableName.IMAGES.value}.id'))
                               )

message_font_association = Table(EnumTableName.MESSAGE_FONT_ASSOCIATION.value, Base.metadata,
                                 Column('font_id', Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id')),
                                 Column('message_id', Integer, ForeignKey(f'{EnumTableName.MESSAGES.value}.id'))
                                 )


class Font(Base):
    __tablename__ = EnumTableName.FONTS.value
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    thumbnail = Column(String, nullable=False)
    post_link = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Boolean, default=True)
    links = relationship(EnumTableName.LINKS.value, secondary=link_font_association, backref=EnumTableName.FONTS.value)
    keys = relationship(EnumTableName.KEYS.value, backref=EnumTableName.FONTS.value)
    images = relationship(EnumTableName.IMAGES.value, secondary=image_font_association,
                          backref=EnumTableName.FONTS.value)


class Link(Base):
    __tablename__ = EnumTableName.LINKS.value
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    fonts = relationship(EnumTableName.FONTS.value, secondary=link_font_association, backref=EnumTableName.LINKS.value)

    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f'Link(id={self.id}, url={self.url})'


class Image(Base):
    __tablename__ = EnumTableName.IMAGES.value
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)

    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f'Image(id={self.id}, url={self.url})'


class Key(Base):
    __tablename__ = EnumTableName.KEYS.value
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False, default=lambda x: x.key.to_lower())
    font_id = Column(Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id'))

    def __init__(self, key: str):
        self.key = key

    def __str__(self):
        return f'Key(id={self.id}, key={self.key})'


class Message(Base):
    __tablename__ = EnumTableName.MESSAGES.value
    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
