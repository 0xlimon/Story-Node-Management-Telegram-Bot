"""Handler module for the start command."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..decorators import admin_only
from ..keyboards.menus import get_main_menu

logger = logging.getLogger(__name__)

@admin_only
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command and main menu navigation.
    Shows the main menu with all available options.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        reply_markup = get_main_menu()
        menu_text = "🤖 Welcome to your Node Management Bot! Choose an option:"
        
        if update.callback_query:
            # If coming from a callback (menu navigation), edit the existing message
            await update.callback_query.edit_message_text(
                text=menu_text,
                reply_markup=reply_markup
            )
            await update.callback_query.answer()
        elif update.message:
            # If it's a new /start command, send a new message
            # Delete any previous menu messages if they exist
            if 'menu_message_id' in context.user_data:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data['menu_message_id']
                    )
                except Exception:
                    pass  # Ignore if message doesn't exist or can't be deleted
            
            # Send new menu and store its message ID
            message = await update.message.reply_text(
                text=menu_text,
                reply_markup=reply_markup
            )
            context.user_data['menu_message_id'] = message.message_id
            
    except Exception as e:
        error_msg = f"❌ Error showing main menu: {str(e)}"
        logger.error(error_msg)
        if update.callback_query:
            await update.callback_query.message.reply_text(error_msg)
            await update.callback_query.answer()
        elif update.message:
            await update.message.reply_text(error_msg)