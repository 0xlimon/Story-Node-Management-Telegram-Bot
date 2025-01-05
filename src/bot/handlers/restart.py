"""Handler module for service restart operations."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ...services import restart_service
from ..decorators import admin_only
from ..keyboards.menus import get_restart_options, get_back_to_main_menu

logger = logging.getLogger(__name__)

@admin_only
async def show_restart_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the restart options menu.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        reply_markup = get_restart_options()
        menu_text = "Choose which service to restart:"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=menu_text,
                reply_markup=reply_markup
            )
            await update.callback_query.answer()
        else:
            # Delete previous restart menu if it exists
            if 'restart_menu_id' in context.user_data:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data['restart_menu_id']
                    )
                except Exception:
                    pass
            
            # Send new menu and store its ID
            restart_menu = await update.message.reply_text(
                text=menu_text,
                reply_markup=reply_markup
            )
            context.user_data['restart_menu_id'] = restart_menu.message_id
            
    except Exception as e:
        error_msg = f"❌ Error showing restart options: {str(e)}"
        logger.error(error_msg)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                error_msg,
                reply_markup=get_back_to_main_menu()
            )
            await update.callback_query.answer()
        else:
            await update.message.reply_text(error_msg)

@admin_only
async def handle_restart_service(update: Update, context: ContextTypes.DEFAULT_TYPE, service_name: str) -> None:
    """
    Handle service restart request.
    
    Args:
        update: The update object
        context: The context object
        service_name: Name of the service to restart
    """
    try:
        # Show processing message
        await update.callback_query.edit_message_text(
            f"🔄 Restarting {service_name} service...",
            reply_markup=None
        )
        await update.callback_query.answer()
        
        # Attempt to restart the service
        success, message = restart_service(service_name)
        
        # Get back to main menu keyboard
        reply_markup = get_back_to_main_menu()
        
        if success:
            status_text = (
                f"✅ {service_name} service restarted successfully.\n\n"
                "Use the button below to return to the main menu."
            )
        else:
            status_text = (
                f"❌ Error restarting {service_name} service: {message}\n\n"
                "Use the button below to return to the main menu."
            )
        
        # Update the message with the result
        await update.callback_query.edit_message_text(
            text=status_text,
            reply_markup=reply_markup
        )
        
    except Exception as e:
        error_msg = (
            f"❌ Error handling restart: {str(e)}\n\n"
            "Use the button below to return to the main menu."
        )
        logger.error(f"Error in handle_restart_service: {e}")
        await update.callback_query.edit_message_text(
            text=error_msg,
            reply_markup=get_back_to_main_menu()
        )