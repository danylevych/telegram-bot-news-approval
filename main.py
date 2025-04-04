from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters
)

from handlers.user import (
    start,
    handle_user_news,
)

from handlers.callbacks import (
    handle_user_confirmation,
    handle_admin_decision,
)

from logger.console_logger import logger
from configs import *


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_user_news))
    app.add_handler(CallbackQueryHandler(handle_user_confirmation, pattern="user_"))
    app.add_handler(CallbackQueryHandler(handle_admin_decision, pattern="approve|reject"))

    logger.info("Bot started and running...")
    app.run_polling()


if __name__ == "__main__":
    main()
