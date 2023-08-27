from typing import List, Dict

from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import (
    Application,
)

from bot.configs.logging import logger
from bot.services.font_service import FontService
from bot.services.google_sheet import GoogleSheetsReader
from bot.services.image_service import ImageService
from bot.services.key_service import KeyService
from bot.services.link_service import LinkService
from bot.services.message_service import MessageService
from bot.services.tag_service import TagService
from bot.utils.db import SessionLocal
from handlers.font_handle import get_conv_handler_font
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


def create_services(db: Session):
    key_service = KeyService(db)
    tag_service = TagService(db)
    link_service = LinkService(db)
    image_service = ImageService(db)
    message_service = MessageService(db)
    font_service = FontService(db)
    return key_service, tag_service, link_service, image_service, message_service, font_service


async def update_data(key_service: KeyService, tag_service: TagService, link_service: LinkService,
                      image_service: ImageService, message_service: MessageService, font_service: FontService):
    reader = GoogleSheetsReader()
    result = reader.update_data(key_service, tag_service, link_service, image_service, message_service, font_service)
    logger.info(f"Updated data from Google Sheets in result: {result}")


def main() -> None:
    db = SessionLocal()
    key_service, tag_service, link_service, image_service, message_service, font_service = create_services(db)
    application = Application.builder().token("6148725172:AAGcJYZkH7B5OudQwALgm4QhyEmyQuoT7G8").build()
    application.add_handler(get_conv_handler_font())
    application.run_polling(allowed_updates=[Update.ALL_TYPES])


if __name__ == "__main__":
    main()
