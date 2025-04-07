from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.user import User
from logger.console_logger import logger
from utils.language_manager import language_manager
from handlers.language import language_command


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    user = User.get(user_id, username)

    if update.effective_user.language_code in language_manager.get_available_languages():
        user.set_language(update.effective_user.language_code)

    logger.info(f"User {user_id} started the bot")

    start_text = language_manager.get_text("user.messages.start", user.get_language())
    await update.message.reply_text(start_text)

    logger.info(f"Start message sent to user {user_id}")



async def handle_user_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Get or create user and update buffer
    user = User.get(user_id, username)
    user.update_buffer(message)

    user_lang = user.get_language()

    confirm_msg_id = user.buffer.get("confirm_msg_id")
    warn_msg_id = user.buffer.get("warn_msg_id")

    if warn_msg_id:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=warn_msg_id)
            logger.info(f"Deleted warning message for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete warning message for user {user_id}: {e}")
        user.buffer["warn_msg_id"] = None

    if confirm_msg_id:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=confirm_msg_id)
            logger.info(f"Deleted confirmation message for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete confirmation message for user {user_id}: {e}")
        user.buffer["confirm_msg_id"] = None

    if user.has_description():
        buttons = [
            [
                InlineKeyboardButton(
                    language_manager.get_text("user.buttons.submit", user_lang),
                    callback_data="user_submit"
                ),
                InlineKeyboardButton(
                    language_manager.get_text("user.buttons.cancel", user_lang),
                    callback_data="user_cancel"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        conformation_msg = await message.reply_text(
            text=language_manager.get_text("user.messages.confirmation", user_lang),
            reply_markup=reply_markup,
        )
        user.set_confirmation_message(conformation_msg.message_id)
        logger.info(f"Confirmation message sent to user {user_id}")

    else:
        logger.info(f"User {user_id} didn't provide a description")
        warning_msg = await message.reply_text(
            text=language_manager.get_text("user.messages.warning_no_description", user_lang),
            reply_markup=None,
        )
        user.set_warning_message(warning_msg.message_id)
        logger.info(f"Warning message sent to user {user_id}")

