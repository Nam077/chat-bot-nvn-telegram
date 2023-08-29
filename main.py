from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import (
    Application,
)

from configs.logging import logger
from handlers.font_handle import FontHandler
from handlers.font_shop_handle import FontShopHandle
from handlers.random_handle import RandomHandle
from handlers.tiktok_handle import get_conv_handler_tiktok
from services.font_crawler_service import FontCrawlerService
from services.font_global_service import FontGlobalService
from services.font_service import FontService
from services.google_sheet import GoogleSheetsReader
from services.image_service import ImageService
from services.key_service import KeyService
from services.link_service import LinkService
from services.message_service import MessageService
from services.setting_service import SettingService
from services.tag_service import TagService
from utils.db import SessionLocal, SessionLocal_2
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
    font_crawler_service = FontCrawlerService()
    return key_service, tag_service, link_service, image_service, message_service, font_service, setting_service, font_crawler_service


def update_data(key_service: KeyService, tag_service: TagService, link_service: LinkService,
                image_service: ImageService, message_service: MessageService, font_service: FontService):
    reader = GoogleSheetsReader()
    result = reader.update_data(key_service, tag_service, link_service, image_service, message_service, font_service)
    logger.info(f"Updated data from Google Sheets in result: {result}")


async def get_all_data(key_service: KeyService):
    return key_service.get_all_keys()


def main() -> None:
    db = SessionLocal()
    db2 = SessionLocal_2()
    font_global_service = FontGlobalService(db2)
    random_handle = RandomHandle(font_global_service=font_global_service)
    (key_service, tag_service, link_service, image_service, message_service, font_service,
     setting_service, font_crawler_service) = create_services(db)
    # update_data(key_service, tag_service, link_service, image_service, message_service, font_service)
    font_handle = FontHandler(key_service, setting_service, font_service)
    font_shop_handle = FontShopHandle(font_crawler_service)
    TELEGRAM_BOT_TOKEN = setting_service.get_setting_by_key('TELEGRAM_BOT_TOKEN').value
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(font_handle.get_conv_handler_font())
    application.add_handler(get_conv_handler_tiktok())
    application.add_handler(font_shop_handle.get_conv_handler_font_shop())
    application.add_handler(random_handle.get_conv_handler_random_font())
    application.run_polling(allowed_updates=[Update.ALL_TYPES])


if __name__ == "__main__":
    main()
