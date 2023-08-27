import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, \
    ConversationHandler, CallbackQueryHandler
import re
from configs.config import TELEGRAM_BOT_USERNAME
from configs.logging import logger
from services.font_global_service import FontGlobalService

FONT_NAME, FONT_PHOTO, FONT_DOWNLOAD = range(3)


class RandomHandle:
    def __init__(self, font_global_service: FontGlobalService):
        self.font_global_service = font_global_service

    async def display_font_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE, limit: int = 10,
                                name: str = None):
        random_fonts = self.font_global_service.get_random_font_by_name_or_category_name(limit=10, name=name)
        if not random_fonts:
            return await update.message.reply_text("Không tìm thấy font nào, vui lòng thử lại.")
        media_group = []
        for random_font in random_fonts:
            media_group.append(InputMediaPhoto(media=random_font.thumbnail + '?w=692&h=461&ssl=1',
                                               caption=f'<b>Name:</b> {random_font.name}\n'
                                                       f'<b>Category:</b> {random_font.category_name}\n'
                                                       f'<b>Downloaded by {TELEGRAM_BOT_USERNAME}</b>',
                                               parse_mode='HTML'))

        keyboard = []
        for random_font in random_fonts:
            keyboard.append([InlineKeyboardButton(random_font.name, callback_data=f"font_{random_font.id}")])
        keyboard.append([InlineKeyboardButton("Exit", callback_data="exit")])
        inline_keyboard = InlineKeyboardMarkup(keyboard)
        await update.message.reply_chat_action('upload_photo')
        await update.message.reply_media_group(media_group)
        await update.message.reply_chat_action('typing')
        await update.message.reply_text("Vui lòng chọn một font để tải về.", reply_markup=inline_keyboard)
        return FONT_DOWNLOAD

    async def random_font_begin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            "Vui lòng gửi một keyword để tìm kiếm font ngẫu nhiên, nếu bỏ qua để random ngẫu nhiên thì gõ /skip.")
        return FONT_NAME

    async def skip_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        logger.info("User %s skipped the font name.", update.message.from_user.first_name)
        await self.display_font_list(update, context)
        return FONT_DOWNLOAD

    async def send_font_random(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        logger.info("Font name from %s: %s", user.first_name, update.message.text)
        font_name = update.message.text
        await self.display_font_list(update, context, name=font_name)
        return FONT_DOWNLOAD

    async def download_font(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        random_font_id = int(update.callback_query.data.split('_')[1])
        random_font = self.font_global_service.get_font_by_id(random_font_id)
        media_photo = []
        for image in random_font.detail_images.split('\n'):
            media_photo.append(InputMediaPhoto(image))
        await update.callback_query.message.reply_media_group(media_photo)
        await update.callback_query.message.reply_text(f"Link download: {random_font.link_drive}",
                                                       reply_markup=InlineKeyboardMarkup(
                                                           [[InlineKeyboardButton("Exit", callback_data="exit")]]))

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            "Tạm biệt!.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def send_call_back_exit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.callback_query.message.reply_text("Tạm biệt!")
        # remove all InlineKeyboardButton
        await update.callback_query.message.edit_reply_markup(reply_markup=None)
        return ConversationHandler.END

    def get_conv_handler_random_font(self) -> ConversationHandler:
        conv_handler_random_font = ConversationHandler(
            entry_points=[CommandHandler("random", self.random_font_begin)],
            states={
                FONT_NAME: [CommandHandler("skip", self.skip_name), MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                                                   self.send_font_random)],
                FONT_DOWNLOAD: [CallbackQueryHandler(self.download_font, pattern="^font_"),
                                CallbackQueryHandler(self.send_call_back_exit, pattern="^exit$")],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        return conv_handler_random_font
