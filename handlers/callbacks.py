from telegram import Update
from telegram.ext import ContextTypes
from models.user import user_buffers
from handlers.admin import forward_to_admins
from configs import CHANNEL_TAG
from logger.console_logger import logger


async def handle_user_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    logger.info(f"Processing confirmation callback from user {user_id}: {query.data}")

    buffer = user_buffers.get(user_id, {})
    await query.answer()

    if query.data == "user_confirm_send":
        logger.info(f"User {user_id} confirmed news submission")
        await forward_to_admins(buffer, context)
        await context.bot.send_message(chat_id=user_id, text="✅ Your news has been sent to the admins.")
        logger.info(f"Confirmation sent to user {user_id}")

    elif query.data == "user_cancel_send":
        logger.info(f"User {user_id} cancelled news submission")
        await context.bot.send_message(chat_id=user_id, text="❌ Your news submission was cancelled.")
        logger.info(f"Cancellation message sent to user {user_id}")

    # Clean up
    logger.debug(f"Clearing buffer for user {user_id}")
    user_buffers[user_id] = {}
    try:
        await query.message.delete()
        logger.debug(f"Deleted confirmation message for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to delete confirmation message for user {user_id}: {e}")


async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = query.from_user.id
    decision = query.data

    logger.info(f"Admin {admin_id} made decision: {decision}")
    await query.answer()

    message = query.message
    caption = message.caption or message.text or ""

    if decision == "approve":
        logger.info(f"Admin {admin_id} approved news")
        try:
            # TODO
            await query.edit_message_text(text=caption + "\n\n✅ Approved and published.")
            logger.info(f"News approved message updated for admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to update message for admin {admin_id}: {e}")

    elif decision == "reject":
        logger.info(f"Admin {admin_id} rejected news")
        try:
            await query.delete_message()
            logger.debug(f"Deleted message for admin {admin_id} after rejection")
        except Exception as e:
            logger.error(f"Failed to delete message for admin {admin_id}, attempting to edit: {e}")
            try:
                await query.edit_message_text(text=caption + "\n\n❌ Rejected.")
                logger.info(f"News rejection message updated for admin {admin_id}")
            except Exception as e2:
                logger.error(f"Failed to update rejection message for admin {admin_id}: {e2}")
