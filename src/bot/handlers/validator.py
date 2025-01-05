"""Handler module for validator-related commands and callbacks."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ...services import fetch_validator_info
from ..decorators import admin_only
from ..keyboards.menus import get_back_to_main_menu

logger = logging.getLogger(__name__)

@admin_only
async def validator_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show detailed validator information.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        info = await fetch_validator_info()
        
        message = "✅ Detailed Validator Information:\n\n"
        
        # Network information
        message += "Network Info:\n"
        message += f"  Network: {info['node_info']['network']}\n"
        message += f"  Moniker: {info['node_info']['moniker']}\n\n"
        
        # Sync status
        message += "Sync Status:\n"
        message += f"  Catching Up: {'Yes' if info['sync_info']['catching_up'] else 'No'}\n"
        message += f"  Latest Block Height: {info['sync_info']['latest_block_height']}\n"
        message += f"  Latest Block Time: {info['sync_info']['latest_block_time']}\n\n"
        
        # Validator information
        message += "Validator Info:\n"
        message += f"  Address: {info['validator_info'].get('address', 'Not available')}\n"
        message += f"  Voting Power: {info['validator_info'].get('voting_power', 'Not available')}\n"
        message += f"  Proposer Priority: {info['validator_info'].get('proposer_priority', 'Not available')}\n"
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=get_back_to_main_menu(),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        error_msg = f"❌ Error fetching validator information: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_main_menu()
        )