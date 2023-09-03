import random
from builtins import str
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove, InputMediaPhoto
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, \
    ConversationHandler, CallbackQueryHandler


class HandleStart:
    async def send_hello(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Xin chào {update.message.from_user.first_name}")

    def get_conv_handler_start(self):
        return ConversationHandler(
            entry_points=[CommandHandler('start', self.send_hello)],
            states={},
            fallbacks=[],
        )
