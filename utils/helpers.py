from collections import defaultdict
from datetime import datetime
import uuid
from telegram import Message
from configs import ADMINS_IDS, ONE_NEWS_ONE_ADMIN
from logger.console_logger import logger

_last_admin_index = -1

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


def get_target_admins():
    """
    Get target admins based on ONE_NEWS_ONE_ADMIN setting.
    If ONE_NEWS_ONE_ADMIN is True, returns a list with a single admin ID using round-robin selection.
    Otherwise, returns all admin IDs.
    """
    global _last_admin_index

    if not ADMINS_IDS:
        logger.warning("No admin IDs configured!")
        return []

    if ONE_NEWS_ONE_ADMIN:
        _last_admin_index = (_last_admin_index + 1) % len(ADMINS_IDS)
        admin_id = ADMINS_IDS[_last_admin_index]
        logger.info(f"ONE_NEWS_ONE_ADMIN enabled, sending to admin {admin_id} (index: {_last_admin_index})")
        return [admin_id]

    logger.info(f"Sending to all {len(ADMINS_IDS)} admins")
    return ADMINS_IDS
