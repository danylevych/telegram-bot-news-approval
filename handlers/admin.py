from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from logger.console_logger import logger
from configs import ADMINS_IDS, ONE_NEWS_ONE_ADMIN
from models.news import News
from models.user import User
from utils.helpers import get_target_admins
from utils.language_manager import language_manager

async def forward_to_admins(user_data, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Forwarding news from user {user_data.get('username')} to admins")

    news = News(user_data)

    target_admins = get_target_admins()
    logger.info(f"Sending news {news.id} to {len(target_admins)} admins")

    content = news.get_content()
    media_group = news.get_media_group()
    documents = news.get_documents()

    for admin_id in target_admins:
        try:
            # Get admin's language preference
            admin = User.get(admin_id, "")
            admin_lang = admin.get_language()

            # Create buttons with localized text
            buttons = [
                [
                    InlineKeyboardButton(
                        language_manager.get_text("admin.buttons.approve", admin_lang),
                        callback_data=f"approve:{news.id}"
                    ),
                    InlineKeyboardButton(
                        language_manager.get_text("admin.buttons.reject", admin_lang),
                        callback_data=f"reject:{news.id}"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            if documents:
                messages = await context.bot.send_media_group(chat_id=admin_id, media=documents)
                for msg in messages:
                    news.track_message(admin_id, "media", msg.message_id)
                logger.debug(f"Documents sent to admin {admin_id}")

            if media_group:
                messages = await context.bot.send_media_group(chat_id=admin_id, media=media_group, caption=content)
                for msg in messages:
                    news.track_message(admin_id, "media", msg.message_id)
                logger.debug(f"Media group sent to admin {admin_id}")
            elif content:
                msg = await context.bot.send_message(chat_id=admin_id, text=content)
                news.track_message(admin_id, "media", msg.message_id)
                logger.debug(f"Text message sent to admin {admin_id}")

            approval_msg = await context.bot.send_message(
                chat_id=admin_id,
                text=language_manager.get_text(
                    "admin.messages.news_payload",
                    admin_lang,
                    user_name=news.username,
                    date=news.get_submision_date(),
                ),
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            news.track_message(admin_id, "approval", approval_msg.message_id)
            logger.debug(f"Approval message sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to send news to admin {admin_id}: {e}")

    logger.info(f"News {news.id} forwarded to {'a single admin' if ONE_NEWS_ONE_ADMIN else 'all admins'}")
    return news.id
