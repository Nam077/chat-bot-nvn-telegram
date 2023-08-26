import logging
import random
from warnings import filterwarnings

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

FONT_NAME, FONT_PHOTO, FONT_DOWNLOAD = range(3)


async def font(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please send the font name you want to search for.")
    return FONT_NAME


async def font_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Font name from %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Now, please send any photo.")
    return FONT_PHOTO


async def download_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("Download", callback_data="download")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click the button to download the font.", reply_markup=reply_markup)
    return FONT_DOWNLOAD


async def download_font(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    random_number = random.randint(1, 100)
    await update.callback_query.message.reply_text(f"Your download number is: {random_number}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token("6148725172:AAGcJYZkH7B5OudQwALgm4QhyEmyQuoT7G8").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("font", font)],
        states={
            FONT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, font_photo)],
            FONT_PHOTO: [MessageHandler(filters.PHOTO, download_button)],
            FONT_DOWNLOAD: [CallbackQueryHandler(download_font, pattern="^download$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
