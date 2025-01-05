"""Handler module for monitoring-related commands and callbacks."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ...services import MonitoringService
from ...utils.config import MONITORING_INTERVAL
from ..decorators import admin_only
from ..keyboards.menus import (
    get_monitor_menu,
    get_back_to_main_menu,
    get_back_to_monitor_menu
)

logger = logging.getLogger(__name__)

@admin_only
async def show_monitor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the monitoring menu with available options.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        reply_markup = get_monitor_menu()
        menu_text = "📝 Monitor Options:"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=menu_text,
                reply_markup=reply_markup
            )
            await update.callback_query.answer()
        else:
            # Delete previous monitoring menu if it exists
            if 'monitor_message_id' in context.user_data:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data['monitor_message_id']
                    )
                except Exception:
                    pass
            
            # Send new menu and store its ID
            monitor_message = await update.message.reply_text(
                text=menu_text,
                reply_markup=reply_markup
            )
            context.user_data['monitor_message_id'] = monitor_message.message_id
            
    except Exception as e:
        error_msg = f"❌ Error showing monitoring menu: {str(e)}"
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
async def activate_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Activate monitoring for the current chat.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        chat_id = update.effective_chat.id
        activated = MonitoringService.activate_monitoring(
            context.chat_data,
            context.job_queue,
            chat_id,
            MONITORING_INTERVAL
        )
        
        if activated:
            message = f"✅ Monitoring activated. You'll receive updates every {MONITORING_INTERVAL // 60} minutes."
        else:
            message = "📝 Monitoring is already active."
        
        await update.callback_query.answer()
        await show_monitor_menu_with_message(update, context, message)
        
    except Exception as e:
        error_msg = f"❌ Error activating monitoring: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_monitor_menu()
        )

@admin_only
async def deactivate_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Deactivate monitoring for the current chat.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        chat_id = update.effective_chat.id
        deactivated = MonitoringService.deactivate_monitoring(
            context.chat_data,
            context.job_queue,
            chat_id
        )
        
        if deactivated:
            message = "❌ Monitoring deactivated."
        else:
            message = "📝 Monitoring is already inactive."
        
        await update.callback_query.answer()
        await show_monitor_menu_with_message(update, context, message)
        
    except Exception as e:
        error_msg = f"❌ Error deactivating monitoring: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_monitor_menu()
        )

@admin_only
async def view_monitoring_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the current monitoring status.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        status = MonitoringService.get_monitoring_status(
            context.chat_data,
            MONITORING_INTERVAL
        )
        
        status_message = "📝 **Monitoring Status:**\n\n"
        status_message += f"• **Active**: {status['status']}\n"
        status_message += f"• **Monitoring Interval**: {status['interval_minutes']} minutes\n"
        
        await update.callback_query.edit_message_text(
            status_message,
            reply_markup=get_back_to_monitor_menu(),
            parse_mode='Markdown'
        )
        await update.callback_query.answer()
        
    except Exception as e:
        error_msg = f"❌ Error fetching monitoring status: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_monitor_menu()
        )

async def show_monitor_menu_with_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message: str
) -> None:
    """
    Show the monitor menu with a custom message.
    
    Args:
        update: The update object
        context: The context object
        message: The message to show above the menu
    """
    reply_markup = get_monitor_menu()
    await update.callback_query.edit_message_text(
        f"{message}\n\n📝 Monitor Options:",
        reply_markup=reply_markup
    )