from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)

from handlers.language import (
    language_command,
    language_callback,
)

from handlers.user import (
    start,
    handle_user_news,
)

from handlers.callbacks import (
    handle_user_confirmation,
    handle_admin_decision,
)

from handlers.help import help_command, help_callback, help_back_callback, submit_help_command

from logger.console_logger import logger
from configs import *


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("submit", submit_help_command))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_user_news))
    app.add_handler(CallbackQueryHandler(handle_user_confirmation, pattern="user_"))
    app.add_handler(CallbackQueryHandler(handle_admin_decision, pattern="approve|reject"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern=r'^help_user|help_admin$'))
    app.add_handler(CallbackQueryHandler(help_back_callback, pattern=r'^help_back$'))
    app.add_handler(CallbackQueryHandler(language_callback, pattern=r'^lang_'))
    logger.info("Bot started and running...")
    app.run_polling()


if __name__ == "__main__":
    main()
