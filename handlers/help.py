from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.user import User
from utils.language_manager import language_manager
from logger.console_logger import logger
from configs import ADMINS_IDS


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command to show general help information"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    user = User.get(user_id, username)
    user_lang = user.get_language()

    # Get help text and check if user is admin
    help_text = language_manager.get_text("user.messages.help.general", user_lang)

    # If user is an admin, add admin note
    if user_id in ADMINS_IDS:
        admin_note = language_manager.get_text("user.messages.help.admin_note", user_lang)
        help_text += admin_note

    # Add buttons for specific help sections
    buttons = [
        [
            InlineKeyboardButton(
                language_manager.get_text("user.buttons.help_user", user_lang),
                callback_data="help_user"
            )
        ]
    ]

    # Add admin help button only for admins
    if user_id in ADMINS_IDS:
        buttons.append([
            InlineKeyboardButton(
                language_manager.get_text("user.buttons.help_admin", user_lang),
                callback_data="help_admin"
            )
        ])

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        text=help_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    logger.info(f"Help command executed for user {user_id}")


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help section callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name

    user = User.get(user_id, username)
    user_lang = user.get_language()
    callback_data = query.data

    # Handle different help sections
    if callback_data == "help_user":
        section_text = language_manager.get_text("help.sections.user", user_lang)
        logger.info(f"Showing user help section to user {user_id}")
    elif callback_data == "help_admin":
        # Only show admin help to admins
        if user_id in ADMINS_IDS:
            section_text = language_manager.get_text("help.sections.admin", user_lang)
            logger.info(f"Showing admin help section to admin {user_id}")
        else:
            await query.answer("You don't have permission to view this section.")
            return
    else:
        # Unknown help section
        await query.answer("Unknown help section.")
        return

    # Back button
    back_button = InlineKeyboardMarkup([[
        InlineKeyboardButton("« Back", callback_data="help_back")
    ]])

    await query.answer()
    await query.edit_message_text(
        text=section_text,
        reply_markup=back_button,
        parse_mode="Markdown"
    )


async def help_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button in help sections"""
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name

    # Just redirect to the main help command
    user = User.get(user_id, username)
    user_lang = user.get_language()

    help_text = language_manager.get_text("user.messages.help.general", user_lang)

    if user_id in ADMINS_IDS:
        admin_note = language_manager.get_text("user.messages.help.admin_note", user_lang)
        help_text += admin_note

    buttons = [
        [
            InlineKeyboardButton(
                language_manager.get_text("user.buttons.help_user", user_lang),
                callback_data="help_user"
            )
        ]
    ]

    if user_id in ADMINS_IDS:
        buttons.append([
            InlineKeyboardButton(
                language_manager.get_text("user.buttons.help_admin", user_lang),
                callback_data="help_admin"
            )
        ])

    reply_markup = InlineKeyboardMarkup(buttons)

    await query.answer()
    await query.edit_message_text(
        text=help_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    logger.info(f"User {user_id} went back to main help")


async def submit_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle specific help about how to submit news"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    user = User.get(user_id, username)
    user_lang = user.get_language()

    help_text = language_manager.get_text("user.messages.help.submit_instructions", user_lang)

    await update.message.reply_text(
        text=help_text,
        parse_mode="Markdown"
    )
    logger.info(f"Submit help command executed for user {user_id}")
