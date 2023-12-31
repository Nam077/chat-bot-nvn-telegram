import requests
import re
from telegram import Update, ReplyKeyboardRemove, InputMediaVideo
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, \
    ConversationHandler
from configs.logging import logger
from configs.config import TELEGRAM_BOT_USERNAME

TIKTOK_LINK, TIKTOK_DOWNLOAD = range(2)


async def tiktok_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Gửi link Tiktok bạn muốn tải, để hủy bỏ gõ /cancel.")
    return TIKTOK_LINK


async def tiktok_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pattern = r'https:\/\/.*\.tiktok\.com'
    user = update.message.from_user
    logger.info("Tiktok link from %s: %s", user.first_name, update.message.text)
    tiktok_link = update.message.text
    if not re.match(pattern, tiktok_link):
        await update.message.reply_text("Link không hợp lệ, vui lòng gửi lại link.")
        return TIKTOK_LINK
    response = requests.get(tiktok_link)
    final_redirected_url = response.url
    if 'tiktok.com' in tiktok_link:
        id_url = re.search(r'/video/(\d+)', final_redirected_url)
        if id_url is None:
            await update.message.reply_text("Video không tồn tại, vui lòng gửi lại link.")
            return TIKTOK_LINK
        else:
            video_id = await update.message.reply_text("Đang tải video, vui lòng chờ...")
            await update.message.reply_chat_action('upload_video')
            id_url = id_url.group(1)
            url = f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={id_url}'
            response = requests.get(url)
            video_url = response.json()['aweme_list'][0]['video']['play_addr']['url_list'][0]
            await update.message.reply_media_group([
                InputMediaVideo(video_url,
                                caption=f'<a href="{tiktok_link}">Tiktok Link</a>\n<b>Downloaded by {TELEGRAM_BOT_USERNAME}</b>',
                                parse_mode='HTML', supports_streaming=True),

            ])
            await video_id.delete()
            print('done')
            return ConversationHandler.END
    else:
        await update.message.reply_text("Video không tồn tại, vui lòng gửi lại link.")
        return TIKTOK_LINK


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Tạm biệt! Hy vọng chúng ta có thể nói chuyện lại một ngày nào đó.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def get_conv_handler_tiktok() -> ConversationHandler:
    conv_handler_tiktok = ConversationHandler(
        entry_points=[CommandHandler("tiktok", tiktok_start)],
        states={
            TIKTOK_LINK: [CommandHandler("cancel", cancel),
                          MessageHandler(filters.TEXT, tiktok_download)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    return conv_handler_tiktok
