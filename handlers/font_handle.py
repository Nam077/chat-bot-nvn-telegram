import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, \
    ConversationHandler, CallbackQueryHandler
from configs.logging import logger
from services.font_service import FontService
from services.key_service import KeyService
from services.setting_service import SettingService


class FontHandler:
    def __init__(self, key_service: KeyService, setting_service: SettingService, font_service: FontService):
        self.FONT_NAME, self.FONT_PHOTO, self.FONT_DOWNLOAD = range(3)
        self.key_service = key_service
        self.setting_service = setting_service
        self.font_service = font_service

    async def font(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Vui lòng gửi tên font bạn muốn tìm kiếm.")
        return self.FONT_NAME

    async def font_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        logger.info("Font name from %s: %s", user.first_name, update.message.text)
        font_name = update.message.text
        if font_name == "azkia":
            await update.message.reply_text("Please send the font photo.")
            return self.FONT_PHOTO
        else:
            await update.message.reply_text("Please send the font name you want to search for.")
            return self.FONT_NAME

    async def download_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        keyboard = [[InlineKeyboardButton("Download", callback_data="download")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Click the button to download the font.", reply_markup=reply_markup)
        return self.FONT_DOWNLOAD

    async def download_font(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        random_number = random.randint(1, 100)
        await update.callback_query.message.reply_text(f"Your download number is: {random_number}")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def get_conv_handler_font(self) -> ConversationHandler:
        conv_handler_font = ConversationHandler(
            entry_points=[CommandHandler("font", self.font)],
            states={
                self.FONT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.font_photo)],
                self.FONT_PHOTO: [MessageHandler(filters.PHOTO, self.download_button)],
                self.FONT_DOWNLOAD: [CallbackQueryHandler(self.download_font, pattern="^download$")],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        return conv_handler_font


if __name__ == "__main__":
    font_bot = FontBot()
    conv_handler_font = font_bot.get_conv_handler_font()

    # Add conv_handler_font to your Telegram updater/dispatcher
    # updater.dispatcher.add_handler(conv_handler_font)
