from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.user import User
from logger.console_logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    user = User.get(user_id, username)

    logger.info(f"User {user_id} started the bot")
    await update.message.reply_text("Send your news (text + optional media). A description is required before submission.")
    logger.info(f"Start message sent to user {user_id}")


async def handle_user_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    # Get or create user and update buffer
    user = User.get(user_id, username)
    user.update_buffer(message)

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
            [InlineKeyboardButton("✅ Submit", callback_data="user_submit"),
             InlineKeyboardButton("❌ Cancel", callback_data="user_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        conformation_msg = await message.reply_text(
            text="📝 You provided a description. Do you want to submit this news for review?",
            reply_markup=reply_markup,
        )
        user.set_confirmation_message(conformation_msg.message_id)
        logger.info(f"Confirmation message sent to user {user_id}")

    else:
        logger.info(f"User {user_id} didn't provide a description")
        warning_msg = await message.reply_text(
            text="⚠️ Please provide a description before submitting your news.",
            reply_markup=None,
        )
        user.set_warning_message(warning_msg.message_id)
        logger.info(f"Warning message sent to user {user_id}")

