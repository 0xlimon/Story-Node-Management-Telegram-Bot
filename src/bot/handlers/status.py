"""Handler module for status-related commands and callbacks."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ...services import (
    check_services_status,
    compare_block_heights,
    fetch_node_status
)
from ...utils.helpers import split_message
from ..decorators import admin_only
from ..keyboards.menus import get_back_to_main_menu

logger = logging.getLogger(__name__)

@admin_only
async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the status command and callback query.
    Shows the current status of the node and services.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        # Get service statuses
        service_statuses = check_services_status()
        
        # Get node status and block height comparison
        block_message, is_synced = await compare_block_heights()
        
        # Get detailed node status
        node_status = await fetch_node_status()
        node_info = node_status.get('result', {}).get('node_info', {})
        sync_info = node_status.get('result', {}).get('sync_info', {})
        validator_info = node_status.get('result', {}).get('validator_info', {})
        
        # Format the status message
        message = "📊 **Node Status:**\n\n"
        
        # Add service status section
        message += "**System Services:**\n"
        for service, status in service_statuses.items():
            message += f"• `{service}`: `{status}`\n"
        message += "\n"
        
        # Add node information section
        message += "**Node Status:**\n"
        message += f"• Node ID: `{node_info.get('id', 'N/A')}`\n"
        message += f"• Listen Address: `{node_info.get('listen_addr', 'N/A')}`\n"
        message += f"• Network: `{node_info.get('network', 'N/A')}`\n"
        message += f"• Version: `{node_info.get('version', 'N/A')}`\n\n"
        
        # Add synchronization information
        message += "**Synchronization Info:**\n"
        message += f"• Latest Block Height: `{sync_info.get('latest_block_height', 'N/A')}`\n"
        message += f"• Latest Block Time: `{sync_info.get('latest_block_time', 'N/A')}`\n"
        message += f"• Catching Up: `{sync_info.get('catching_up', False)}`\n\n"
        
        # Add validator information
        message += "**Validator Info:**\n"
        message += f"• Address: `{validator_info.get('address', 'N/A')}`\n"
        message += f"• Voting Power: `{validator_info.get('voting_power', 'N/A')}`\n"
        message += f"• Proposer Priority: `{validator_info.get('proposer_priority', 'N/A')}`\n\n"
        
        # Add block synchronization status
        message += block_message
        
        # Get back to main menu keyboard
        reply_markup = get_back_to_main_menu()
        
        # Handle message length and send
        if len(message) <= 4096:
            if update.callback_query:
                # Edit existing message if coming from callback
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                await update.callback_query.answer()
            else:
                # Delete previous status message if it exists
                if 'status_message_id' in context.user_data:
                    try:
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=context.user_data['status_message_id']
                        )
                    except Exception:
                        pass
                
                # Send new status message and store its ID
                status_message = await update.message.reply_text(
                    message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                context.user_data['status_message_id'] = status_message.message_id
        else:
            # For long messages, split them but maintain navigation
            messages = split_message(message)
            for idx, msg in enumerate(messages):
                if idx == 0:
                    if update.callback_query:
                        await update.callback_query.edit_message_text(
                            msg,
                            reply_markup=reply_markup if idx == len(messages) - 1 else None,
                            parse_mode='Markdown'
                        )
                    else:
                        # Delete previous status messages if they exist
                        if 'status_message_ids' in context.user_data:
                            for msg_id in context.user_data['status_message_ids']:
                                try:
                                    await context.bot.delete_message(
                                        chat_id=update.effective_chat.id,
                                        message_id=msg_id
                                    )
                                except Exception:
                                    pass
                        
                        context.user_data['status_message_ids'] = []
                        status_message = await update.message.reply_text(
                            msg,
                            reply_markup=reply_markup if idx == len(messages) - 1 else None,
                            parse_mode='Markdown'
                        )
                        context.user_data['status_message_ids'].append(status_message.message_id)
                else:
                    status_message = await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=msg,
                        reply_markup=reply_markup if idx == len(messages) - 1 else None,
                        parse_mode='Markdown'
                    )
                    if 'status_message_ids' in context.user_data:
                        context.user_data['status_message_ids'].append(status_message.message_id)
            
            if update.callback_query:
                await update.callback_query.answer()
            
    except Exception as e:
        error_msg = f"❌ Error fetching status: {str(e)}"
        logger.error(error_msg)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                error_msg,
                reply_markup=get_back_to_main_menu()
            )
            await update.callback_query.answer()
        else:
            await update.message.reply_text(error_msg)