import asyncio

import schedule
import time

from configs.config import TELEGRAM_BOT_USERNAME
from services.font_global_service import FontGlobalService

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, \
    ConversationHandler, CallbackQueryHandler, Application,


def job():
    print("I'm working...")


class ScheduleSendFont:
    def __init__(self, app: Application, font_global_service: FontGlobalService, id_group):
        self.app = app
        self.font_global_service = font_global_service
        self.id_group = id_group

    async def schedule_send_font(self):
        while True:
            await asyncio.sleep(5)  # Schedule every 5 seconds
            asyncio.create_task(self.send_font())

    async def send_font(self):
        context = self.app.get_context()
        list_font = self.font_global_service.get_random_font_by_name_or_category_name(limit=1, name=None)
        # cứ 1 phút gửi 1 font
        random_font = list_font[0]
        media_photo = [InputMediaPhoto(image) for image in random_font.detail_images.split('\n')]
        await context.bot.send_chat_action(chat_id=self.id_group, action='upload_photo')
        await context.bot.send_media_group(chat_id=self.id_group, media=media_photo)
        buttons = [
            [InlineKeyboardButton("Download", url=random_font.link_drive)]]
        inline_keyboard = InlineKeyboardMarkup(buttons)

        await context.bot.send_message(chat_id=self.id_group,
                                       text=f"Chào mọi người\n<b>Tên:</b> {random_font.name}<b>\n"
                                            f"<a href='{random_font.link_drive}'>Link download</a></b>\n<b>Category:</b> "
                                            f"{random_font.category_name}\n<b>Downloaded by {TELEGRAM_BOT_USERNAME}</b>",
                                       parse_mode='HTML', reply_markup=inline_keyboard
                                       )
