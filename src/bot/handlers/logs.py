"""Handler module for log-related commands and callbacks."""

import os
import logging
import tempfile
import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

from ..decorators import admin_only
from ..keyboards.menus import (
    get_log_options,
    get_log_filter_options,
    get_back_to_main_menu
)

logger = logging.getLogger(__name__)

async def fetch_and_save_logs(service: str, lines: int = 100, level: Optional[str] = None) -> str:
    """
    Fetch logs from journalctl and save them to a temporary file.
    
    Args:
        service: The service to fetch logs for
        lines: Number of lines to fetch
        level: Optional log level to filter by
        
    Returns:
        Path to the temporary file containing logs
        
    Raises:
        Exception: If log fetching fails
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log') as temp_file:
        command = f"journalctl -u {service} -n {lines} --no-pager"
        if level:
            command += f" -p {level}"
            
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=temp_file,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        return temp_file.name

@admin_only
async def show_log_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the log options menu.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        reply_markup = get_log_options()
        menu_text = "Choose which logs to view:"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=menu_text,
                reply_markup=reply_markup
            )
            await update.callback_query.answer()
        else:
            # Delete previous log menu if it exists
            if 'log_menu_id' in context.user_data:
                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=context.user_data['log_menu_id']
                    )
                except Exception:
                    pass
            
            # Send new menu and store its ID
            log_menu = await update.message.reply_text(
                text=menu_text,
                reply_markup=reply_markup
            )
            context.user_data['log_menu_id'] = log_menu.message_id
            
    except Exception as e:
        error_msg = f"❌ Error showing log options: {str(e)}"
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
async def show_log_filter_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    service: str
) -> None:
    """
    Show the log filter options menu.
    
    Args:
        update: The update object
        context: The context object
        service: The service to show filter options for
    """
    try:
        reply_markup = get_log_filter_options(service)
        await update.callback_query.edit_message_text(
            "Select log level to filter:",
            reply_markup=reply_markup
        )
        await update.callback_query.answer()
    except Exception as e:
        error_msg = f"❌ Error showing filter options: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_main_menu()
        )

@admin_only
async def handle_log_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle log filter selection.
    
    Args:
        update: The update object
        context: The context object
    """
    query = update.callback_query
    _, service, level = query.data.split('_')[2:]
    
    if level == 'all':
        level = None
    
    await view_logs(update, context, service, level)

@admin_only
async def view_logs(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    service: str,
    level: Optional[str] = None
) -> None:
    """
    View logs for a specific service.
    
    Args:
        update: The update object
        context: The context object
        service: The service to view logs for
        level: Optional log level to filter by
    """
    try:
        temp_file_path = await fetch_and_save_logs(service, lines=100, level=level)
        
        # Clean up previous log files if they exist
        if 'log_file_message_id' in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['log_file_message_id']
                )
            except Exception:
                pass
        
        # Send the log file
        with open(temp_file_path, 'rb') as log_file:
            level_text = f" ({level} level)" if level else ""
            message = await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=log_file,
                filename=f"{service}_logs{level_text}.txt",
                caption=f"Recent logs for {service}{level_text}"
            )
            context.user_data['log_file_message_id'] = message.message_id
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Update the menu message with navigation options
        await update.callback_query.edit_message_text(
            f"Logs for {service} have been sent as a file. Use the buttons below for more options:",
            reply_markup=get_back_to_main_menu()
        )
        await update.callback_query.answer()
        
    except Exception as e:
        error_msg = f"❌ Error fetching logs for {service}: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_main_menu()
        )
        await update.callback_query.answer()