from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
from logger.console_logger import logger

class User:
    """Class to manage user data and message buffers"""

    # Class-level storage of all users
    _users = {}  # user_id -> User object

    def __init__(self, user_id: int, username: str = None):
        """Initialize a user with empty buffer"""
        self.id = user_id
        self.username = username
        self.buffer = {
            "text": "",
            "caption": "",
            "photo": [],
            "video": [],
            "document": [],
            "timestamp": datetime.now(),
            "user_id": user_id,
            "username": username,
            "warn_msg_id": None,
            "confirm_msg_id": None,
        }

        # Register in users dictionary
        User._users[user_id] = self
        logger.debug(f"Created new user object for user_id {user_id}")

    @classmethod
    def get(cls, user_id: int, username: str = None) -> 'User':
        """Get or create a user object"""
        if user_id not in cls._users:
            return cls(user_id, username)
        return cls._users[user_id]

    def update_buffer(self, message):
        """Update the user's buffer with new message data"""
        self.buffer["username"] = message.from_user.username or message.from_user.first_name or self.buffer["username"]
        self.buffer["timestamp"] = datetime.now()

        # Update text or caption
        if message.text:
            self.buffer["text"] = message.text
            logger.debug(f"Updated text for user {self.id}")

        if message.caption:
            self.buffer["caption"] = message.caption
            logger.debug(f"Updated caption for user {self.id}")

        # Update media
        if message.photo:
            file_id = message.photo[-1].file_id
            self.buffer["photo"].append(file_id)
            logger.debug(f"Added photo with file_id {file_id} to user {self.id}'s buffer")

        if message.document:
            file_id = message.document.file_id
            self.buffer["document"].append(file_id)
            logger.debug(f"Added document with file_id {file_id} to user {self.id}'s buffer")

        if message.video:
            file_id = message.video.file_id
            self.buffer["video"].append(file_id)
            logger.debug(f"Added video with file_id {file_id} to user {self.id}'s buffer")

        logger.info(f"Buffer updated for user {self.id}")
        return self.buffer

    def has_content(self) -> bool:
        """Check if the user buffer has actual content"""
        has_text = bool(self.buffer.get("text") or self.buffer.get("caption"))
        has_media = bool(self.buffer.get("photo") or self.buffer.get("video") or self.buffer.get("document"))
        return has_text and has_media

    def has_description(self) -> bool:
        """Check if the user buffer has a description"""
        return bool(self.buffer.get("text") or self.buffer.get("caption"))

    def set_warning_message(self, message_id: int):
        """Set ID of warning message sent to user"""
        self.buffer["warn_msg_id"] = message_id

    def set_confirmation_message(self, message_id: int):
        """Set ID of confirmation message sent to user"""
        self.buffer["confirm_msg_id"] = message_id

    def clear(self):
        """Clear user buffer after submission"""
        warn_id = self.buffer.get("warn_msg_id")
        confirm_id = self.buffer.get("confirm_msg_id")

        self.buffer = {
            "text": "",
            "caption": "",
            "photo": [],
            "video": [],
            "document": [],
            "timestamp": datetime.now(),
            "user_id": self.id,
            "username": self.buffer.get("username"),
            "warn_msg_id": warn_id,
            "confirm_msg_id": confirm_id,
        }
        logger.debug(f"Cleared buffer for user {self.id}")

        try:
            del User._users[self.id]
            logger.debug(f"Removed user {self.id} from registry")
        except KeyError:
            logger.error(f"User {self.id} not found in user registry")

    def set_language(self, lang: str):
        """Set user's preferred language"""
        self.language = lang

    def get_language(self) -> str:
        """Get user's preferred language"""
        return getattr(self, 'language', 'en')
