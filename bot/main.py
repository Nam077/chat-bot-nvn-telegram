from telegram import Update
from telegram.ext import (
    Application,
)
from handlers.font_handle import get_conv_handler_font
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


def main() -> None:
    application = Application.builder().token("6148725172:AAGcJYZkH7B5OudQwALgm4QhyEmyQuoT7G8").build()
    application.add_handler(get_conv_handler_font())
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
