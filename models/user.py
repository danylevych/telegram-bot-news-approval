from collections import defaultdict
from datetime import datetime

# User buffer to store messages in memory
# user_buffers = {
#     user_id: {
#         "text": "Optional text message content",
#         "caption": "Optional media caption",
#
#         "photo": ["file_id1", "file_id2", ...],
#         "video": ["file_id1", ...],
#         "document": ["file_id1", ...],
#
#         "username": "username or first_name",
#         "timestamp": datetime_object,
#
#
#         "warn_msg_id": 12345,
#         "confirm_msg_id": 67890,
#     }
# }

user_buffers = defaultdict(dict)
