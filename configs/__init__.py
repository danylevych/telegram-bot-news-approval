import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN   : str       = os.getenv("BOT_TOKEN")
ADMINS_IDS  : list[int] = list(map(int, os.getenv("ADMINS_IDS").split(",")))
CHANNEL_TAG : str       = os.getenv("CHANNEL_TAG")
