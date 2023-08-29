import requests
import re
from telegram import Update, ReplyKeyboardRemove, InputMediaVideo
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, \
    ConversationHandler
from configs.logging import logger
from configs.config import TELEGRAM_BOT_USERNAME
from services.font_crawler_service import FontCrawlerService
import asyncio

FONT_SHOP_LINK, FONT_SHOP_DOWNLOAD = range(2)
import os


class FontShopHandle:
    def __init__(self, font_crawler_service: FontCrawlerService):
        self.font_crawler_service = font_crawler_service

    async def font_shop_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Gửi link Fontshop bạn muốn tải, để hủy bỏ gõ /cancel.")
        return FONT_SHOP_LINK

    async def font_shop_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        pattern = r'https:\/\/www\.fontshop\.com\/families\/.*'
        user = update.message.from_user
        logger.info("Fontshop link from %s: %s", user.first_name, update.message.text)
        font_shop_link = update.message.text

        # Lưu trữ user_id trong context
        user_id = update.message.from_user.id
        context.user_data['user_id'] = user_id

        if not re.match(pattern, font_shop_link):
            await update.message.reply_text("Link không hợp lệ, vui lòng gửi lại link.")
            return FONT_SHOP_LINK
        id_delete = await update.message.reply_text("Đang tải font, tôi sẽ gửi cho bạn khi xử lý xong...")
        asyncio.create_task(self.save_font_crawler(font_shop_link, update, context, id_delete))
        return ConversationHandler.END

    async def save_font_crawler(self, font_shop_link: str, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                id_delete):
        self.font_crawler_service.set_crawl_url(font_shop_link)
        font_crawler = self.font_crawler_service.save_font_data()
        if font_crawler is not None:
            file = open(font_crawler, 'rb')
            user_id = context.user_data.get('user_id')
            if user_id:
                await id_delete.delete()
                message_noti = await context.bot.send_message(chat_id=user_id, text="Đã tải xong, đang gửi cho bạn...")
                await context.bot.send_chat_action(chat_id=user_id, action='upload_document')
                await context.bot.send_document(chat_id=user_id, document=file,caption="Mật khẩu giải nén là nvnfont")
                await message_noti.delete()
                await context.bot.send_message(chat_id=user_id,
                                               text="Để chuyển đổi đúng định dạng bạn hãy truy cập vào trang "
                                                    "https://transfonter.org để chuyển "
                                                    "đổi.")
            file.close()
            os.remove(font_crawler)
            return

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            "Tạm biệt! Hy vọng chúng ta có thể nói chuyện lại một ngày nào đó.", reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def get_conv_handler_font_shop(self) -> ConversationHandler:
        conv_handler_font_shop = ConversationHandler(
            entry_points=[CommandHandler("crawler", self.font_shop_start)],
            states={
                FONT_SHOP_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.font_shop_download)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        return conv_handler_font_shop
