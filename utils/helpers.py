from datetime import datetime
from telegram import Message
from logger.console_logger import logger


def what_was_sent(message: Message):
    results = []
    if message.photo:
        results.append("photo")
    if message.document:
        results.append("document")
    if message.video:
        results.append("video")

    logger.debug(f"Message from user {message.from_user.id} contains: {', '.join(results) or 'no media'}")
    return results


def update_buffer(user_id, message: Message, user_buffers):
    logger.info(f"Updating buffer for user {user_id}")

    buffer = user_buffers.get(user_id, {}) or {
        "text": "",
        "photo": [],
        "document": [],
        "video": [],
        "caption": "",
        "timestamp": datetime.now(),
    }

    buffer["username"] = message.from_user.username or message.from_user.first_name
    buffer["text"] = message.text or buffer.get("text", '')
    buffer["caption"] = message.caption or buffer.get("caption", '')

    types = what_was_sent(message)
    for t in types:
        if t == "photo":
            file_id = message.photo[-1].file_id
            buffer["photo"].append(file_id)
            logger.debug(f"Added photo with file_id {file_id} to user {user_id}'s buffer")

        elif t == "document":
            file_id = message.document.file_id
            buffer["document"].append(file_id)
            logger.debug(f"Added document with file_id {file_id} to user {user_id}'s buffer")

        elif t == "video":
            file_id = message.video.file_id
            buffer["video"].append(file_id)
            logger.debug(f"Added video with file_id {file_id} to user {user_id}'s buffer")

    logger.info(f"Buffer updated for user {user_id}")
    return buffer
