from typing import List, Dict

from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import (
    Application,
)

from bot.configs.logging import logger
from bot.handlers.random_handle import RandomHandle
from bot.handlers.tiktok_handle import get_conv_handler_tiktok
from bot.services.font_global_service import FontGlobalService
from bot.services.font_service import FontService
from bot.services.google_sheet import GoogleSheetsReader
from bot.services.image_service import ImageService
from bot.services.key_service import KeyService
from bot.services.link_service import LinkService
from bot.services.message_service import MessageService
from bot.services.setting_service import SettingService
from bot.services.tag_service import TagService
from bot.utils.db import SessionLocal, SessionLocal_2
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
    setting_service = SettingService(db)
    return key_service, tag_service, link_service, image_service, message_service, font_service, setting_service


async def update_data(key_service: KeyService, tag_service: TagService, link_service: LinkService,
                      image_service: ImageService, message_service: MessageService, font_service: FontService):
    reader = GoogleSheetsReader()
    result = reader.update_data(key_service, tag_service, link_service, image_service, message_service, font_service)
    logger.info(f"Updated data from Google Sheets in result: {result}")


def main() -> None:
    db = SessionLocal()
    db2 = SessionLocal_2()
    font_global_service = FontGlobalService(db2)
    random_handle = RandomHandle(font_global_service=font_global_service)
    (key_service, tag_service, link_service, image_service, message_service, font_service,
     setting_service) = create_services(db)
    TELEGRAM_BOT_TOKEN = setting_service.get_setting_by_key('TELEGRAM_BOT_TOKEN').value
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(get_conv_handler_font())
    application.add_handler(get_conv_handler_tiktok())
    application.add_handler(random_handle.get_conv_handler_random_font())
    application.run_polling(allowed_updates=[Update.ALL_TYPES])


if __name__ == "__main__":
    main()
