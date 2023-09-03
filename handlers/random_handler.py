import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CallbackContext,
)
from configs.config import TELEGRAM_BOT_USERNAME
from services.font_global_service import FontGlobalService

FONT_NAME, FONT_DOWNLOAD = range(2)


class RandomFontHandler:
    def __init__(self, font_global_service: FontGlobalService):
        self.font_global_service = font_global_service
        self.messages_to_cleanup = []  # List to store messages that need cleanup
        self.media_group_to_cleanup = []
        self.messages_to_cleanup_exit = []
        self.font_name = None

    async def add_message_to_cleanup(self, message):
        self.messages_to_cleanup.append(message)

    async def add_media_group_to_cleanup(self, media_group):
        self.media_group_to_cleanup.append(media_group)

    async def cleanup_messages(self):
        await asyncio.gather(*(message.delete() for message in self.messages_to_cleanup))
        self.messages_to_cleanup = []

    async def cleanup_media_groups(self):
        for media_group in self.media_group_to_cleanup:
            await asyncio.gather(*(message.delete() for message in media_group))
        self.media_group_to_cleanup = []

    async def cleanup_exit_button(self, update, context: CallbackContext) -> None:
        await asyncio.gather(*(message.delete() for message in self.messages_to_cleanup_exit))
        self.messages_to_cleanup_exit = []

    async def display_random_fonts(self, update, context, limit=10, name=None):
        random_fonts = self.font_global_service.get_random_font_by_name_or_category_name(limit=limit, name=name)
        if not random_fonts:
            return await update.message.reply_text("Không tìm thấy font nào, vui lòng thử lại.")

        media_group = []
        await update.message.reply_chat_action('upload_photo')

        for random_font in random_fonts:
            media_group.append(
                InputMediaPhoto(
                    media=random_font.thumbnail + '?w=692&h=461&ssl=1',
                    caption=f'<b>Name:</b> {random_font.name}\n'
                            f'<b>Category:</b> {random_font.category_name}\n'
                            f'<b>Downloaded by {TELEGRAM_BOT_USERNAME}</b>',
                    parse_mode='HTML'
                )
            )

        buttons_per_row = 2
        keyboard = [
            [
                InlineKeyboardButton(random_font.name, callback_data=f"font_{random_font.id}")
                for random_font in random_fonts[i: i + buttons_per_row]
            ]
            for i in range(0, len(random_fonts), buttons_per_row)
        ]
        keyboard.append([InlineKeyboardButton("Thoát", callback_data="exit")])
        inline_keyboard = InlineKeyboardMarkup(keyboard)

        media_group_message = await update.message.reply_media_group(media_group)
        await self.add_media_group_to_cleanup(media_group_message)
        await update.message.reply_chat_action('typing')
        await self.add_message_to_cleanup(update.message)
        message_button = await update.message.reply_text(
            "Vui lòng chọn một font để tải về. Nếu muốn xem thêm thì gõ /view_more.",
            reply_markup=inline_keyboard)
        self.messages_to_cleanup.append(message_button)
        return FONT_DOWNLOAD

    async def exit_and_cleanup(self, update, context: CallbackContext) -> None:
        await self.cleanup_exit_button(update, context)
        await self.cleanup_messages()
        await self.cleanup_media_groups()
        await update.callback_query.message.reply_text("Tạm biệt!")

    async def handle_font_download(self, update, context: CallbackContext) -> int | None:
        if update.callback_query.data == "exit":
            await self.exit_and_cleanup(update, context)
            return ConversationHandler.END

        await self.cleanup_exit_button(update, context)
        random_font_id = int(update.callback_query.data.split('_')[1])
        random_font = self.font_global_service.get_font_by_id(random_font_id)

        media_photo = [InputMediaPhoto(image) for image in random_font.detail_images.split('\n')]
        await update.callback_query.message.reply_chat_action('upload_photo')
        await update.callback_query.message.reply_media_group(media_photo)
        buttons = [
            [InlineKeyboardButton("Download", url=random_font.link_drive)]]
        inline_keyboard = InlineKeyboardMarkup(buttons)

        await update.callback_query.message.reply_text(
            f"Chào {update.callback_query.from_user.first_name}\n<b>Tên:</b> {random_font.name}<b>\n"
            f"<a href='{random_font.link_drive}'>Link download</a></b>\n<b>Category:</b> "
            f"{random_font.category_name}\n<b>Downloaded by {TELEGRAM_BOT_USERNAME}</b>",
            parse_mode='HTML', reply_markup=inline_keyboard
        )
        exit_button = InlineKeyboardButton("Exit", callback_data="exit")
        inline_keyboard = InlineKeyboardMarkup([[exit_button]])
        exit_button = await update.callback_query.message.reply_text(
            "Bấm exit để thoát khỏi", reply_markup=inline_keyboard
        )
        self.messages_to_cleanup_exit.append(exit_button)

    # Trong lớp RandomFontHandler:
    async def handle_view_more(self, update, context: CallbackContext) -> None:
        print(self.font_name)
        await self.display_random_fonts(update, context, limit=10, name=self.font_name)
        return FONT_DOWNLOAD

    def get_random_font_handler(self) -> ConversationHandler:
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("random", self.start_random_font)],
            states={
                FONT_NAME: [CommandHandler("skip", self.skip_font_name),
                            MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_font_name)],
                FONT_DOWNLOAD: [CallbackQueryHandler(self.handle_font_download, pattern="^font_|exit$"),
                                CommandHandler("view_more", self.handle_view_more)]

            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        return conv_handler

    async def start_random_font(self, update, context: CallbackContext) -> int:
        message_start = await update.message.reply_text(
            "Vui lòng gửi một keyword để tìm kiếm font ngẫu nhiên, nếu bỏ qua để random ngẫu nhiên thì gõ /skip."
        )
        self.messages_to_cleanup.append(message_start)
        return FONT_NAME

    async def cancel(self, update, context: CallbackContext) -> int:
        await self.cleanup_exit_button(update, context)
        await self.cleanup_messages()
        await self.cleanup_media_groups()
        return ConversationHandler.END

    async def skip_font_name(self, update, context: CallbackContext) -> int:

        await self.cleanup_messages()
        await self.cleanup_media_groups()
        await self.display_random_fonts(update, context)
        return FONT_DOWNLOAD

    async def receive_font_name(self, update, context: CallbackContext) -> int:
        await self.cleanup_messages()
        await self.cleanup_media_groups()
        self.font_name = update.message.text
        await self.display_random_fonts(update, context, name=self.font_name)
        return FONT_DOWNLOAD
