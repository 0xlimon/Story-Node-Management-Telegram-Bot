"""Handler module for help command and callback."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ..decorators import admin_only
from ..keyboards.menus import get_back_to_main_menu

logger = logging.getLogger(__name__)

@admin_only
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the help command and callback.
    Shows available commands and bot documentation.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        help_text = """
📚 Available commands:
• /start - Start the bot and show main menu

📜 Menu options:
• 📊 Status - Check node status
• 📜 Logs - View recent logs
• 🔄 Restart Services - Restart story or story-geth service
• 💻 System Info - Show system information
• 📝 Monitor - Toggle continuous monitoring
• 📈 Performance - View node performance metrics
• 🌐 Network - Show network statistics
• ✅ Validator - Show validator information
• ❔ Help - Display this help message

📗 Additional Information:
• This bot is based on the GitHub project:
  https://github.com/0xlimon/Story-Node-Management-Telegram-Bot

💡 Feedback and Suggestions:
We appreciate your feedback! If you have any suggestions, feature requests, or issues, please feel free to:
1. Open an issue on our GitHub repository
2. Submit a pull request with your improvements
3. Contact the developer directly


Thank you for using our Story Node Management Bot!
"""
        # Get back to main menu keyboard
        reply_markup = get_back_to_main_menu()
        
        if update.callback_query:
            # Edit existing message if coming from callback
            await update.callback_query.edit_message_text(
                help_text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            await update.callback_query.answer()
        else:
            # Delete previous help message if it exists
            if 'help_message_id' in context.user_data:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data['help_message_id']
                    )
                except Exception:
                    pass
            
            # Send new help message and store its ID
            help_message = await update.message.reply_text(
                help_text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            context.user_data['help_message_id'] = help_message.message_id
            
    except Exception as e:
        error_msg = f"❌ Error showing help: {str(e)}"
        logger.error(error_msg)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                error_msg,
                reply_markup=get_back_to_main_menu()
            )
            await update.callback_query.answer()
        else:
            await update.message.reply_text(error_msg)