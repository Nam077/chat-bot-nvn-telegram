import asyncio
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaAudio
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, ContextTypes, \
    CallbackQueryHandler

from configs.config import TELEGRAM_BOT_USERNAME
from utils.youtube_downloader import YoutubeMusicConverter

YOUTUBE_LINK, YOUTUBE_DOWNLOAD = range(2)


def check_url(url):
    pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.match(pattern, url)


class YoutubeDownloadHandler:
    def __init__(self):
        self.youtube_dl = YoutubeMusicConverter()

    async def youtube_download_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Gửi link Youtube bạn muốn tải, để hủy bỏ gõ /cancel.")
        return YOUTUBE_LINK

    async def youtube_download_mp3(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        link = update.message.text
        if not check_url(link):
            await update.message.reply_text("Link không hợp lệ, vui lòng gửi lại link.")
            return YOUTUBE_LINK
        process = await update.message.reply_text("Đang xử lý, vui lòng chờ...")
        self.youtube_dl.url = link
        self.youtube_dl.vt = 'mp3'
        option_download = self.youtube_dl.get_option_download()

        if option_download:
            context.user_data['option_download'] = option_download
            context.user_data['link'] = link
            links = option_download.get('links')
            buttons_per_row = 3
            keyboard = [
                [
                    InlineKeyboardButton(link.get('q') + " " + link.get('size'),
                                         callback_data=f"yt_mp3_{link.get('f')}_{link.get('k')}")
                    for link in links[i: i + buttons_per_row]
                ]
                for i in range(0, len(links), buttons_per_row)
            ]
            keyboard.append([InlineKeyboardButton("Thoát", callback_data="exit")])
            inline_keyboard = InlineKeyboardMarkup(keyboard)
            await process.delete()
            await update.message.reply_text("Vui lòng chọn chất lượng để tải về.", reply_markup=inline_keyboard)
            return YOUTUBE_DOWNLOAD
        else:
            await update.message.reply_text("Không tìm thấy video, vui lòng thử lại.")
            return YOUTUBE_LINK

    async def youtube_download_mp4(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        link = update.message.text
        if not check_url(link):
            await update.message.reply_text("Link không hợp lệ, vui lòng gửi lại link.")
            return YOUTUBE_LINK
        process = await update.message.reply_text("Đang xử lý, vui lòng chờ...")
        self.youtube_dl.url = link
        self.youtube_dl.vt = 'mp4'
        option_download = self.youtube_dl.get_option_download()

        if option_download:
            context.user_data['option_download'] = option_download
            context.user_data['link'] = link
            links = option_download.get('links')
            buttons_per_row = 3
            keyboard = [
                [
                    InlineKeyboardButton(link.get('q') + " " + link.get('size'),
                                         callback_data=f"yt_mp3_{link.get('f')}_{link.get('k')}")
                    for link in links[i: i + buttons_per_row]
                ]
                for i in range(0, len(links), buttons_per_row)
            ]
            keyboard.append([InlineKeyboardButton("Thoát", callback_data="exit")])
            inline_keyboard = InlineKeyboardMarkup(keyboard)
            await process.delete()
            await update.message.reply_text("Vui lòng chọn chất lượng để tải về.", reply_markup=inline_keyboard)
            return YOUTUBE_DOWNLOAD
        else:
            await update.message.reply_text("Không tìm thấy video, vui lòng thử lại.")
            return YOUTUBE_LINK

    async def youtube_covert(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.callback_query.data == "exit":
            await update.callback_query.message.reply_text("Tạm biệt!")
            return ConversationHandler.END
        downloading = await update.callback_query.message.reply_text("Đang tải video, vui lòng chờ...")
        option_download = context.user_data.get('option_download')
        chose = {
            'f': update.callback_query.data.split('_')[2],
            'k': update.callback_query.data.split('_')[3]
        }
        print(chose)
        link = self.youtube_dl.get_download_url(option_download_data=option_download, chose=chose)
        print(link)
        await update.callback_query.message.reply_chat_action('upload_audio')
        media_group_message = []
        link_user = context.user_data.get('link')
        media_group_message.append(
            InputMediaAudio(link.get('url'), filename=link.get('filename'),
                            caption=f'<a href="{link_user}">Youtube Link</a>\n' + \
                                    f'<b>Downloaded by {TELEGRAM_BOT_USERNAME}</b>',
                            parse_mode='HTML'))
        asyncio.create_task(update.callback_query.message.reply_media_group(media_group_message))
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        await update.message.reply_text("Tạm biệt!")
        return ConversationHandler.END

    def get_download_mp3_conv_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[CommandHandler('yt_mp3', self.youtube_download_start)],
            states={
                YOUTUBE_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.youtube_download_mp3)],
                YOUTUBE_DOWNLOAD: [CallbackQueryHandler(self.youtube_covert, pattern="^yt_mp3_"), ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

    def get_download_mp4_conv_handler(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[CommandHandler('yt_mp4', self.youtube_download_start)],
            states={
                YOUTUBE_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.youtube_download_mp4)],
                YOUTUBE_DOWNLOAD: [CallbackQueryHandler(self.youtube_covert, pattern="^yt_mp4_"), ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
