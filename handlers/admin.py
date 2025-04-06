from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from logger.console_logger import logger
from configs import ADMINS_IDS, ONE_NEWS_ONE_ADMIN
from models.news import News
from utils.helpers import get_target_admins

async def forward_to_admins(user_data, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Forwarding news from user {user_data.get('username')} to admins")

    news = News(user_data)

    buttons = [
        [InlineKeyboardButton("✅ Approve", callback_data=f"approve:{news.id}"),
         InlineKeyboardButton("❌ Reject", callback_data=f"reject:{news.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    content = news.get_content()
    media_group = news.get_media_group()

    target_admins = get_target_admins()
    logger.info(f"Sending news {news.id} to {len(target_admins)} admins with {len(media_group)} media items")

    for admin_id in target_admins:
        try:
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
                text=news.get_payload(),
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            news.track_message(admin_id, "approval", approval_msg.message_id)
            logger.debug(f"Approval message sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to send news to admin {admin_id}: {e}")

    logger.info(f"News {news.id} forwarded to {'a single admin' if ONE_NEWS_ONE_ADMIN else 'all admins'}")
    return news.id
