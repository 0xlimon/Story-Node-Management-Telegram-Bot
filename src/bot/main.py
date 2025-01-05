"""Main module for the Story Validator Bot."""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler
)

from ..utils.config import BOT_TOKEN, LOGGING_CONFIG
from .handlers import callback_handlers, command_handlers

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context) -> None:
    """
    Handle errors in the bot.
    
    Args:
        update: The update that caused the error
        context: The context that caused the error
    """
    logger.error(f"Error occurred: {context.error}")
    try:
        if update.effective_message:
            await update.effective_message.reply_text(
                "An error occurred. Please try again later."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def create_application() -> Application:
    """
    Create and configure the bot application.
    
    Returns:
        The configured Application instance
    """
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register command handlers
    for command, handler in command_handlers.items():
        application.add_handler(CommandHandler(command, handler))
    
    # Register callback query handler
    application.add_handler(
        CallbackQueryHandler(
            lambda u, c: callback_handlers[u.callback_query.data](u, c)
            if u.callback_query.data in callback_handlers else None
        )
    )
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    return application

def main() -> None:
    """
    Main function to run the bot.
    """
    try:
        # Create and run the application
        application = create_application()
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == '__main__':
    main()