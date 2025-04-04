from telegram import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from logger.console_logger import logger
from configs import ADMINS_IDS


async def forward_to_admins(news, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Forwarding news from user to admins")

    buttons = [
        [InlineKeyboardButton("✅ Approve", callback_data="approve"),
         InlineKeyboardButton("❌ Reject", callback_data="reject")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    caption = ""
    if news.get("caption"):
        caption += f"{news['caption']}\n\n"
    if news.get("text"):
        caption += f"{news['text']}"

    media_group = []
    for media_type in ["photo", "video", "document"]:
        for file_id in news.get(media_type, []):
            if media_type == "photo":
                media_group.append(InputMediaPhoto(file_id))
                logger.debug(f"Added photo with file_id {file_id} to media group")
            elif media_type == "video":
                media_group.append(InputMediaVideo(file_id))
                logger.debug(f"Added video with file_id {file_id} to media group")
            elif media_type == "document":
                media_group.append(InputMediaDocument(file_id))
                logger.debug(f"Added document with file_id {file_id} to media group")

    payload = (
        f"*News from @{news['username']}*\n"
        f"*Submitted at:* {news['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
    )

    logger.info(f"Sending news to {len(ADMINS_IDS)} admins with {len(media_group)} media items")

    for admin_id in ADMINS_IDS:
        try:
            if media_group:
                await context.bot.send_media_group(chat_id=admin_id, media=media_group, caption=caption)
                logger.debug(f"Media group sent to admin {admin_id}")

            await context.bot.send_message(
                chat_id=admin_id,
                text=payload,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            logger.debug(f"Approval message sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to send news to admin {admin_id}: {e}")

    logger.info(f"News forwarded to all admins")
