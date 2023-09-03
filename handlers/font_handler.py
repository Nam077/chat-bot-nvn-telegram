import random
from builtins import str
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, \
    ConversationHandler, CallbackQueryHandler

from configs.config import TELEGRAM_BOT_USERNAME
from configs.logging import logger
from models.models import Font
from services.font_service import FontService
from services.key_service import KeyService
from services.setting_service import SettingService


async def send_image_font(update: Update, context: ContextTypes.DEFAULT_TYPE, font: Font):
    images = font.images
    random_images = random.sample(images, min(10, len(images)))
    media_photo = [InputMediaPhoto(media=images.url, caption=font.name) for images in random_images]
    await update.message.reply_chat_action('upload_photo')
    await update.message.reply_media_group(media_photo)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
            InlineKeyboardButton("Option 2", callback_data="2"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [InlineKeyboardButton("Option 3", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)
    await update.message.reply_text(
        f"Tạm biệt! {user.first_name}.\n"
    )
    return ConversationHandler.END


async def download_font(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    random_number = random.randint(1, 100)
    await update.callback_query.message.reply_text(f"Your download number is: {random_number}")
    return ConversationHandler.END


def get_link_download(font: Font):
    links = font.links
    random_links = random.sample(links, min(10, len(links)))
    buttons = []
    for link in random_links:
        buttons.append([InlineKeyboardButton("Download", url=link.url)])
    return buttons


async def send_one_font(update: Update, context: ContextTypes.DEFAULT_TYPE, font: Font) -> int:
    message = (
        f"Xin chào {update.message.from_user.first_name}\n"
        f"<b>Tên:</b> {font.name}\n"
        f"<b>Link bài viết:</b> <a href='{font.post_link}'>Link</a>\n"
        f"<b>Downloaded by {TELEGRAM_BOT_USERNAME}</b>"

    )
    buttons = get_link_download(font)
    buttons_markup = InlineKeyboardMarkup(buttons)
    await send_image_font(update, context, font)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=buttons_markup)
    return ConversationHandler.END


class FontHandler:
    def __init__(self, key_service: KeyService, setting_service: SettingService, font_service: FontService):
        self.FONT_NAME, self.FONT_PHOTO, self.FONT_DOWNLOAD = range(3)
        self.key_service = key_service
        self.setting_service = setting_service
        self.font_service = font_service
        self.key_list = self.key_service.get_all_keys()
        self.chunk_name_string = self.font_service.get_chunk_name_font()

    async def get_font_by_message(self, message: str):
        result = []
        for key in self.key_list:
            if key.value in message.lower():
                result.append(key.font)
                print(key.font)

        return result

    async def send_list_font(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        for chunk in self.chunk_name_string:
            await update.message.reply_text(chunk)
        await update.message.reply_text("Vui lòng gửi tên font bạn muốn tìm kiếm. Hoặc gửi /cancel để hủy.")
        return self.FONT_NAME

    async def font(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            "Vui lòng gửi tên font bạn muốn tìm kiếm.\nLấy danh sách font bằng cách gửi /list.\nHoặc gửi /cancel để hủy.")
        return self.FONT_NAME

    async def font_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None | Any:
        user = update.message.from_user
        logger.info("Font name from %s: %s", user.first_name, update.message.text)
        font_name = update.message.text
        font = await self.get_font_by_message(font_name)
        if not font:
            await update.message.reply_text("Không tìm thấy font nào, vui lòng thử lại.")
            return self.FONT_NAME
        if self.setting_service.get_setting_by_value_bool('MULTIPLE_FONT'):
            if 1 < len(font) <= 10:
                return await self.send_multiple_font(update, context, font)
            elif len(font) > 10:
                return await self.send_multiple_font_string(update, context, font)
        else:
            return await send_one_font(update, context, font[0])

    async def download_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        keyboard = [[InlineKeyboardButton("Download", callback_data="download")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Click the button to download the font.", reply_markup=reply_markup)
        return self.FONT_DOWNLOAD

    def get_conv_handler_font(self) -> ConversationHandler:
        conv_handler_font = ConversationHandler(
            entry_points=[CommandHandler("fontvh", self.font)],
            states={
                self.FONT_NAME: [CommandHandler("list", self.send_list_font),
                                 MessageHandler(filters.TEXT & ~filters.COMMAND, self.font_photo)],
                self.FONT_PHOTO: [MessageHandler(filters.PHOTO, self.download_button)],
                self.FONT_DOWNLOAD: [CallbackQueryHandler(download_font, pattern="^download$")],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        return conv_handler_font

    async def send_multiple_font(self, update: Update, context: ContextTypes.DEFAULT_TYPE, font):
        pass

    async def send_multiple_font_string(self, update: Update, context: ContextTypes.DEFAULT_TYPE, font):
        pass
