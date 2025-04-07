from telegram import Update
from telegram.ext import ContextTypes
from models.user import User
from handlers.admin import forward_to_admins
from configs import CHANNEL_TAG
from logger.console_logger import logger
from models.news import News
from utils.language_manager import language_manager


async def handle_user_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    logger.info(f"Processing confirmation callback from user {user_id}: {query.data}")

    user = User.get(user_id, username)
    user_lang = user.get_language()
    await query.answer()

    if query.data == "user_submit":
        news_id = await forward_to_admins(user.buffer, context)
        await query.edit_message_text(language_manager.get_text("user.messages.news_submitted", user_lang))
        logger.info(f"News from user {user_id} submitted successfully")
        user.clear()

    elif query.data == "user_cancel":
        user.clear()
        await query.edit_message_text(language_manager.get_text("user.messages.submission_canceled", user_lang))
        logger.info(f"Submission canceled by user {user_id}")


async def handle_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = query.from_user.id
    admin_name = query.from_user.username or query.from_user.first_name or f"ID:{admin_id}"

    admin = User.get(admin_id, admin_name)
    admin_lang = admin.get_language()

    # Extract decision and news_id from callback data
    parts = query.data.split(":")
    decision, news_id = parts[0], parts[1] if len(parts) > 1 else None

    logger.info(f"Admin {admin_name} ({admin_id}) made decision: {decision} for news {news_id}")
    await query.answer()

    news = News.get_by_id(news_id)

    if not news:
        logger.error(f"News {news_id} not found")
        await query.edit_message_text(text=language_manager.get_text("admin.messages.news_unavailable", admin_lang))
        return

    if news.status != "pending":
        status_key = f"common.status.{news.status}"
        await query.edit_message_text(
            text=language_manager.get_text(
                "admin.messages.news_already_processed",
                admin_lang,
                status=language_manager.get_text(status_key, admin_lang),
                admin_name=news.deciding_admin_name
            )
        )
        return

    message = query.message
    caption = message.caption or message.text or ""

    if decision == "approve":
        news.mark_approved(admin_id, admin_name)

        try:
            # TODO: Implement publishing to channel
            await query.edit_message_text(text=caption + "\n\n" + language_manager.get_text("admin.messages.approved", admin_lang))
            logger.info(f"News approved message updated for admin {admin_name}")

            # Update other admins
            for other_admin_id, messages in news.admin_messages.items():
                if other_admin_id != admin_id and messages["approval_message"]:
                    try:
                        other_admin = User.get(other_admin_id, "")
                        other_lang = other_admin.get_language()
                        await context.bot.edit_message_text(
                            chat_id=other_admin_id,
                            message_id=messages["approval_message"],
                            text=caption + f"\n\n✅ " + language_manager.get_text(
                                "admin.messages.news_already_processed",
                                other_lang,
                                status=language_manager.get_text("common.status.approved", other_lang),
                                admin_name=admin_name
                            )
                        )
                    except Exception as e:
                        logger.error(f"Failed to update message for admin {other_admin_id}: {e}")
        except Exception as e:
            logger.error(f"Failed to update message for admin {admin_name}: {e}")

    elif decision == "reject":
        news.mark_rejected(admin_id, admin_name)

        # Delete ALL messages across ALL admins
        for target_admin_id, messages in news.admin_messages.items():
            target_admin = User.get(target_admin_id, "")
            target_lang = target_admin.get_language()

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
                            text=language_manager.get_text("admin.messages.news_rejected_by", target_lang, admin_name=admin_name)
                        )
                    except Exception as e2:
                        logger.error(f"Failed to update message for admin {target_admin_id}: {e2}")

        try:
            await query.delete_message()
            logger.debug(f"Deleted approval message for admin {admin_name}")
        except Exception as e:
            logger.error(f"Failed to delete message for admin {admin_name}: {e}")
            try:
                await query.edit_message_text(text=caption + "\n\n" + language_manager.get_text("admin.messages.rejected", admin_lang))
            except Exception as e2:
                logger.error(f"Failed to update rejection message for admin {admin_name}: {e2}")
