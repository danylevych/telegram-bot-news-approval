from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.helpers import update_buffer
from models.user import user_buffers

from logger.console_logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"User {user.id} started the bot")
    await update.message.reply_text("Send your news (text + optional media). A description is required before submission.")
    logger.info(f"Start message sent to user {user.id}")


async def handle_user_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = message.from_user.id
    username = message.from_user.username

    logger.info(f"Received news from user {user_id} ({username})")

    buffer = update_buffer(user_id, message, user_buffers)
    user_buffers[user_id] = buffer

    has_description = buffer.get("text") or buffer.get("caption")
    logger.info(f"User {user_id} news has description: {has_description}")

    # Delete previous warning if it exists
    if "warn_msg_id" in buffer:
        try:
            logger.info(f"Deleting previous warning message for user {user_id}")
            await context.bot.delete_message(chat_id=user_id, message_id=buffer["warn_msg_id"])
        except Exception as e:
            logger.error(f"Failed to delete warning message for user {user_id}: {e}")
        buffer.pop("warn_msg_id", None)

    # Delete previous confirmation if it exists
    if "confirm_msg_id" in buffer:
        try:
            logger.info(f"Deleting previous confirmation message for user {user_id}")
            await context.bot.delete_message(chat_id=user_id, message_id=buffer["confirm_msg_id"])
        except Exception as e:
            logger.error(f"Failed to delete confirmation message for user {user_id}: {e}")
        buffer.pop("confirm_msg_id", None)

    if not has_description:
        logger.info(f"Sending description warning to user {user_id}")
        warning = await message.reply_text("⚠️ Please include a description or caption before submitting your news.")
        buffer["warn_msg_id"] = warning.message_id
        logger.info(f"Warning message sent to user {user_id}, message_id: {warning.message_id}")
    else:
        logger.info(f"Sending confirmation prompt to user {user_id}")
        confirm_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, submit", callback_data="user_confirm_send"),
             InlineKeyboardButton("❌ No, cancel", callback_data="user_cancel_send")]
        ])
        confirmation = await message.reply_text(
            "📝 You provided a description. Do you want to submit this news for review?",
            reply_markup=confirm_buttons
        )
        buffer["confirm_msg_id"] = confirmation.message_id
        logger.info(f"Confirmation message sent to user {user_id}, message_id: {confirmation.message_id}")
