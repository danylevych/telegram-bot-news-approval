import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN          : str       = os.getenv("BOT_TOKEN")
ADMINS_IDS         : list[int] = list(map(int, os.getenv("ADMINS_IDS").split(",")))
CHANNEL_TAG        : str       = os.getenv("CHANNEL_TAG")
ONE_NEWS_ONE_ADMIN : bool      = os.getenv("ONE_NEWS_ONE_ADMIN", "False").lower() in ('true', 'yes', '1')
