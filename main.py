import asyncio
import threading
from warnings import filterwarnings

from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import (
    Application, )
from telegram.warnings import PTBUserWarning

from configs.logging import logger
from handlers.font_handler import FontHandler
from handlers.font_shop_handler import FontShopHandle
from handlers.handler_start import HandleStart
from handlers.random_handler import RandomFontHandler
from handlers.schedule_send_font import ScheduleSendFont
from handlers.tiktok_handler import get_conv_handler_tiktok
from handlers.youtube_downloader_handler import YoutubeDownloadHandler
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


async def get_all_list_group_bot_join(update: Update, context):
    list_group = await context.bot.get_chat_member(chat_id=-1001829709246, user_id=update.message.from_user.id)
    print(list_group)


def main() -> None:
    db = SessionLocal()
    db2 = SessionLocal_2()
    font_global_service = FontGlobalService(db2)
    random_handle = RandomFontHandler(font_global_service=font_global_service)
    (key_service, tag_service, link_service, image_service, message_service, font_service,
     setting_service, font_crawler_service) = create_services(db)
    font_handle = FontHandler(key_service, setting_service, font_service)
    font_shop_handle = FontShopHandle(font_crawler_service)
    start_handler = HandleStart()
    youtube_download = YoutubeDownloadHandler()
    telegram_bot_token = setting_service.get_setting_by_key('TELEGRAM_BOT_TOKEN').value
    telegram_bot_token_2 = setting_service.get_setting_by_key('TELEGRAM_BOT_TOKEN_2').value
    application_1 = Application.builder().token(telegram_bot_token).build()
    application_1.add_handler(font_handle.get_conv_handler_font())
    application_1.add_handler(get_conv_handler_tiktok())
    application_1.add_handler(font_shop_handle.get_conv_handler_font_shop())
    application_1.add_handler(random_handle.get_random_font_handler())
    application_1.add_handler(youtube_download.get_download_mp3_conv_handler())
    application_1.add_handler(start_handler.get_conv_handler_start())
    application_1.add_handler(youtube_download.get_download_mp4_conv_handler())
    application_2 = Application.builder().token(telegram_bot_token_2).build()
    application_2.add_handler(start_handler.get_conv_handler_start())
    schedule_send_font = ScheduleSendFont(font_global_service, -1001829709246)
    application_2.add_handler(schedule_send_font.get_schedule_send_font_handler())
    application_2.add_handler(schedule_send_font.get_main_con())
    thread1 = threading.Thread(target=run_bot, args=(application_1,))
    thread2 = threading.Thread(target=run_bot, args=(application_2,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


def run_bot(application):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.run_polling(allowed_updates=[Update.ALL_TYPES]))


def run_schedule_send_font(schedule_send_font):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(schedule_send_font.schedule_send_font())


if __name__ == "__main__":
    main()
