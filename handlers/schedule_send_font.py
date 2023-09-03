import asyncio
from datetime import time as dt_time

import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import RetryAfter
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, CallbackContext

from configs.config import TELEGRAM_BOT_USERNAME
from services.font_global_service import FontGlobalService


def job():
    print("I'm working...")


class ScheduleSendFont:
    def __init__(self, font_global_service: FontGlobalService, id_group):
        self.font_global_service = font_global_service
        self.id_group = id_group

    async def send_font_random(self, context: CallbackContext) -> int | None:
        try:
            random_font = self.font_global_service.get_random_font_by_name_or_category_name(limit=1)[0]
            first_image = random_font.detail_images.split('\n')[0]

            buttons = [
                [InlineKeyboardButton("Download", url=random_font.link_drive)]
            ]
            inline_keyboard = InlineKeyboardMarkup(buttons)

            text_message = f"Chào mọi người\n<b>Tên:</b> {random_font.name}<b>\n" \
                           f"<a href='{random_font.link_drive}'>Link download</a></b>\n<b>Category:</b> " \
                           f"{random_font.category_name}\n<b>Downloaded by {TELEGRAM_BOT_USERNAME}</b>"

            await context.bot.send_chat_action(chat_id=self.id_group, action='upload_photo')
            await context.bot.send_photo(chat_id=self.id_group, photo=first_image, caption=text_message,
                                         parse_mode='HTML', reply_markup=inline_keyboard)

        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
            await self.send_font_random(context)

    async def send_font_main(self, context: CallbackContext) -> int | None:
        asyncio.create_task(self.send_font_random(context))
        return ConversationHandler.END

    async def get_group_id(self, update: Update, context: CallbackContext) -> int | None:
        if not await self.check_if_admin(update, context):
            return ConversationHandler.END
        chat_id = update.message.chat_id
        await update.message.reply_text(f"ID nhóm của bạn là: {chat_id}")
        return ConversationHandler.END

    async def check_id_group_available(self, update: Update, context: CallbackContext) -> bool:
        try:
            # kiểm tra xem bot có trong nhóm không
            chat_member = await context.bot.get_chat_member(chat_id=self.id_group, user_id=context.bot.id)
            if not chat_member:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        return True

    async def start_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_id = update.message.from_user.id
        if user_id != 2022028420:
            await update.message.reply_text("Bạn không có quyền sử dụng lệnh này.")
            return ConversationHandler.END
        if update.message.chat.type != 'group' and update.message.chat.type != 'supergroup':
            await update.message.reply_text("Không thể sử dụng lệnh này trong nhóm.")
            return ConversationHandler.END
        id_group = context.args[0] if len(context.args) > 0 else None
        if id_group is None:
            await update.message.reply_text("Bạn chưa nhập id nhóm.")
            return ConversationHandler.END
        self.id_group = id_group
        if not await self.check_id_group_available(update, context):
            await update.message.reply_text("Nhóm không tồn tại.")
            return ConversationHandler.END
        if not await self.check_if_admin(update, context):
            await update.message.reply_text("Bạn không phải là admin.")
            return ConversationHandler.END
        context.job_queue.run_daily(self.send_font_random,
                                    time=dt_time(hour=7, minute=0, second=0,
                                                 tzinfo=pytz.timezone('Asia/Ho_Chi_Minh')))

        # Gửi font vào lúc 7 giờ tối theo giờ địa phương 'Asia/Ho_Chi_Minh'
        context.job_queue.run_daily(self.send_font_random,
                                    time=dt_time(hour=19, minute=0, second=0,
                                                 tzinfo=pytz.timezone('Asia/Ho_Chi_Minh')))
        await update.message.reply_text("Đã bắt đầu lên lịch gửi font.")
        return ConversationHandler.END

    def get_schedule_send_font_handler(self) -> ConversationHandler:
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("schedule_send_font", self.start_schedule)],
            states={},
            fallbacks=[],
        )
        return conv_handler

    async def check_if_admin(self, update: Update, context: CallbackContext) -> bool:
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        chat_admins = await context.bot.get_chat_administrators(chat_id)
        for admin in chat_admins:
            if admin.user.id == user_id:
                return True
        return False

    def get_main_con(self) -> ConversationHandler:

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("admin", self.get_group_id)],
            states={},
            fallbacks=[],
        )
        return conv_handler
