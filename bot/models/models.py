from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

Base = declarative_base()


class EnumTableName(Enum):
    FONTS = "fonts"
    LINKS = "links"
    IMAGES = "images"
    KEYS = "keys"
    MESSAGES = "messages"
    SETTINGS = "settings"
    LINK_FONT_ASSOCIATION = "link_font_association"
    IMAGE_FONT_ASSOCIATION = "image_font_association"
    MESSAGE_FONT_ASSOCIATION = "message_font_association"


# Define association tables as mapped classes
class LinkFontAssociation(Base):
    __tablename__ = EnumTableName.LINK_FONT_ASSOCIATION.value
    font_id = Column(Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id'), primary_key=True)
    link_id = Column(Integer, ForeignKey(f'{EnumTableName.LINKS.value}.id'), primary_key=True)


class ImageFontAssociation(Base):
    __tablename__ = EnumTableName.IMAGE_FONT_ASSOCIATION.value
    font_id = Column(Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id'), primary_key=True)
    image_id = Column(Integer, ForeignKey(f'{EnumTableName.IMAGES.value}.id'), primary_key=True)


class MessageFontAssociation(Base):
    __tablename__ = EnumTableName.MESSAGE_FONT_ASSOCIATION.value
    font_id = Column(Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id'), primary_key=True)
    message_id = Column(Integer, ForeignKey(f'{EnumTableName.MESSAGES.value}.id'), primary_key=True)


class Font(Base):
    __tablename__ = EnumTableName.FONTS.value
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    thumbnail = Column(String, nullable=False)
    post_link = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Boolean, default=True)
    keys = relationship("Key", backref="font")
    font_links = relationship("Link", secondary=LinkFontAssociation.__table__, backref="linked_fonts")
    font_images = relationship("Image", secondary=ImageFontAssociation.__table__, backref="linked_fonts")
    font_messages = relationship("Message", secondary=MessageFontAssociation.__table__, backref="linked_fonts")


class Link(Base):
    __tablename__ = EnumTableName.LINKS.value
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)

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
    value = Column(String, nullable=False)
    font_id = Column(Integer, ForeignKey(f'{EnumTableName.FONTS.value}.id'), nullable=True)

    def __init__(self, key: str):
        self.key = key
        self.value = key.lower()

    def __str__(self):
        return f'Key(id={self.id}, key={self.key})'


class Message(Base):
    __tablename__ = EnumTableName.MESSAGES.value
    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)

    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f'Message(id={self.id}, value={self.value})'


class Settings(Base):
    __tablename__ = EnumTableName.SETTINGS.value
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False, default='')

    def __init__(self, key: str):
        self.key = key

    def __str__(self):
        return f'Settings(id={self.id}, key={self.key})'
