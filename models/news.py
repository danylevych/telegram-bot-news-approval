from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict
import uuid
from logger.console_logger import logger

class News:
    # Registry of all news items
    _all_news = {}  # news_id -> News object

    def __init__(self, user_data: Dict[str, Any]):
        """Initialize a news item from user buffer data"""
        self.id = str(uuid.uuid4())
        self.status = "pending"  # pending, approved, rejected
        self.timestamp = user_data.get("timestamp", datetime.now())
        self.username = user_data.get("username", "Unknown")
        self.submitted_by = user_data.get("user_id")

        # Content
        self.text = user_data.get("text", "")
        self.caption = user_data.get("caption", "")
        self.photos = user_data.get("photo", [])
        self.videos = user_data.get("video", [])
        self.documents = user_data.get("document", [])

        # Decision tracking
        self.deciding_admin_id = None
        self.deciding_admin_name = None

        # Message tracking for each admin
        self.admin_messages = defaultdict(lambda: {"media_messages": [], "approval_message": None})

        # Add to registry
        News._all_news[self.id] = self
        logger.info(f"Created new news item {self.id} from user {self.username}")

    def get_content(self) -> str:
        """Get the full content of the news item"""
        content = ""
        if self.caption:
            content += f"{self.caption}\n\n"
        if self.text:
            content += f"{self.text}"
        return content

    def get_media_group(self):
        """Convert stored media IDs to InputMedia objects for sending"""
        from telegram import InputMediaPhoto, InputMediaVideo

        media_group = []

        for photo_id in self.photos:
            media_group.append(InputMediaPhoto(photo_id))

        for video_id in self.videos:
            media_group.append(InputMediaVideo(video_id))

        return media_group

    def get_documents(self):
        from telegram import InputMediaDocument
        return [InputMediaDocument(doc_id) for doc_id in self.documents]


    def get_payload(self) -> str:
        """Get formatted payload for admin approval"""
        return (
            f"*News from @{self.username}*\n"
            f"*Submitted at:* {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def get_submision_date(self) -> str:
        """Get formatted submission date"""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def track_message(self, admin_id: int, message_type: str, message_id: int):
        """Track a message sent to an admin"""
        if message_type == "media":
            self.admin_messages[admin_id]["media_messages"].append(message_id)
        elif message_type == "approval":
            self.admin_messages[admin_id]["approval_message"] = message_id

    def mark_approved(self, admin_id: int, admin_name: str):
        """Mark news as approved by an admin"""
        self.status = "approved"
        self.deciding_admin_id = admin_id
        self.deciding_admin_name = admin_name
        logger.info(f"News {self.id} marked as approved by admin {admin_name} ({admin_id})")

        News.clear_news(self.id)

    def mark_rejected(self, admin_id: int, admin_name: str):
        """Mark news as rejected by an admin"""
        self.status = "rejected"
        self.deciding_admin_id = admin_id
        self.deciding_admin_name = admin_name
        logger.info(f"News {self.id} marked as rejected by admin {admin_name} ({admin_id})")

        News.clear_news(self.id)


    @classmethod
    def get_by_id(cls, news_id: str) -> Optional['News']:
        """Get a news item by ID"""
        return cls._all_news.get(news_id)

    @classmethod
    def clear_news(cls, news_id: str):
        try:
            del News._all_news[news_id]
            logger.debug(f"Deleted rejected news {news_id} from registry")
        except KeyError:
            logger.error(f"Failed to delete news {news_id} from registry: not found")
