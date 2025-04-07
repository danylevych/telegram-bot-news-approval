from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from models.user import User
from utils.language_manager import language_manager
from logger.console_logger import logger


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /language command to let users select their preferred language"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    user = User.get(user_id, username)
    user_lang = user.get_language()

    # Create language selection buttons
    buttons = [
        [InlineKeyboardButton(language_manager.get_text("user.buttons.language_en", user_lang), callback_data="lang_en")],
        [InlineKeyboardButton(language_manager.get_text("user.buttons.language_uk", user_lang), callback_data="lang_uk")]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        language_manager.get_text("user.messages.select_language", user_lang),
        reply_markup=reply_markup
    )
    logger.info(f"Language selection menu sent to user {user_id}")


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the language selection callback"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name
    lang_code = query.data.split("_")[1]

    user = User.get(user_id, username)
    user.set_language(lang_code)

    await query.answer()
    await query.edit_message_text(language_manager.get_text("user.messages.language_set", lang_code))
    logger.info(f"User {user_id} set language to {lang_code}")
