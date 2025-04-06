from telegram import Update
from telegram.ext import ContextTypes
from models.user import User
from handlers.admin import forward_to_admins
from configs import CHANNEL_TAG
from logger.console_logger import logger
from models.news import News


async def handle_user_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    logger.info(f"Processing confirmation callback from user {user_id}: {query.data}")

    user = User.get(user_id, username)
    await query.answer()

    if query.data == "user_submit":
        news_id = await forward_to_admins(user.buffer, context)
        await query.edit_message_text(f"✅ Your news has been submitted for approval!")
        logger.info(f"News from user {user_id} submitted successfully")
        user.clear()

    elif query.data == "user_cancel":
        user.clear()
        await query.edit_message_text("❌ Submission canceled. Feel free to start over.")
        logger.info(f"Submission canceled by user {user_id}")


async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = query.from_user.id
    admin_name = query.from_user.username or query.from_user.first_name or f"ID:{admin_id}"

    # Extract decision and news_id from callback data
    parts = query.data.split(":")
    decision, news_id = parts[0], parts[1] if len(parts) > 1 else None

    logger.info(f"Admin {admin_name} ({admin_id}) made decision: {decision} for news {news_id}")
    await query.answer()

    news = News.get_by_id(news_id)

    if not news:
        logger.error(f"News {news_id} not found")
        await query.edit_message_text(text="This news item is no longer available.")
        return

    if news.status != "pending":
        await query.edit_message_text(
            text=f"This news was already {news.status} by admin @{news.deciding_admin_name}"
        )
        return

    message = query.message
    caption = message.caption or message.text or ""

    if decision == "approve":
        news.mark_approved(admin_id, admin_name)

        try:
            # TODO: Implement publishing to channel
            await query.edit_message_text(text=caption + "\n\n✅ Approved.")
            logger.info(f"News approved message updated for admin {admin_name}")

            # Update other admins
            for other_admin_id, messages in news.admin_messages.items():
                if other_admin_id != admin_id and messages["approval_message"]:
                    try:
                        await context.bot.edit_message_text(
                            chat_id=other_admin_id,
                            message_id=messages["approval_message"],
                            text=caption + f"\n\n✅ Already approved by admin @{admin_name}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to update message for admin {other_admin_id}: {e}")
        except Exception as e:
            logger.error(f"Failed to update message for admin {admin_name}: {e}")

    elif decision == "reject":
        news.mark_rejected(admin_id, admin_name)

        # Delete ALL messages across ALL admins
        for target_admin_id, messages in news.admin_messages.items():
            for msg_id in messages["media_messages"]:
                try:
                    await context.bot.delete_message(chat_id=target_admin_id, message_id=msg_id)
                    logger.debug(f"Deleted media message for admin {target_admin_id}")
                except Exception as e:
                    logger.error(f"Failed to delete message for admin {target_admin_id}: {e}")

            if messages["approval_message"]:
                if target_admin_id == admin_id:
                    continue

                try:
                    await context.bot.delete_message(
                        chat_id=target_admin_id,
                        message_id=messages["approval_message"]
                    )
                    logger.debug(f"Deleted approval message for admin {target_admin_id}")
                except Exception as e:
                    try:
                        await context.bot.edit_message_text(
                            chat_id=target_admin_id,
                            message_id=messages["approval_message"],
                            text=f"❌ News was rejected by admin @{admin_name}"
                        )
                    except Exception as e2:
                        logger.error(f"Failed to update message for admin {target_admin_id}: {e2}")

        try:
            await query.delete_message()
            logger.debug(f"Deleted approval message for admin {admin_name}")
        except Exception as e:
            logger.error(f"Failed to delete message for admin {admin_name}: {e}")
            try:
                await query.edit_message_text(text=caption + "\n\n❌ Rejected.")
            except Exception as e2:
                logger.error(f"Failed to update rejection message for admin {admin_name}: {e2}")
