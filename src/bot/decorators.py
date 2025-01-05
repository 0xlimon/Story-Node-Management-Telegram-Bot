"""Decorators for the Telegram bot handlers."""

import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from ..utils.config import ADMIN_ID

logger = logging.getLogger(__name__)

def admin_only(func):
    """
    Decorator to restrict handler access to admin only.
    
    Args:
        func: The handler function to wrap
        
    Returns:
        The wrapped function that checks for admin access
    """
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            logger.warning(f"Unauthorized access attempt from user ID: {user_id}")
            
            if update.callback_query:
                await update.callback_query.answer(
                    "Sorry, you are not authorized to use this bot.",
                    show_alert=True
                )
            else:
                await update.message.reply_text(
                    "Sorry, you are not authorized to use this bot."
                )
            return
        
        return await func(update, context, *args, **kwargs)
    
    return wrapped