import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, \
    ConversationHandler, CallbackQueryHandler
from configs.logging import logger

FONT_NAME, FONT_PHOTO, FONT_DOWNLOAD = range(3)


async def font(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please send the font name you want to search for.")
    return FONT_NAME


async def font_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Font name from %s: %s", user.first_name, update.message.text)
    font_name = update.message.text
    if font_name == "azkia":
        await update.message.reply_text("Please send the font photo.")
        return FONT_PHOTO
    else:
        await update.message.reply_text("Please send the font name you want to search for.")
        return FONT_NAME


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


def get_conv_handler_font() -> ConversationHandler:
    conv_handler_font = ConversationHandler(
        entry_points=[CommandHandler("font", font)],
        states={
            FONT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, font_photo)],
            FONT_PHOTO: [MessageHandler(filters.PHOTO, download_button)],
            FONT_DOWNLOAD: [CallbackQueryHandler(download_font, pattern="^download$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    return conv_handler_font
