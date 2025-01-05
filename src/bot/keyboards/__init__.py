"""Keyboard menus package for the Story Validator Bot."""

from .menus import (
    get_main_menu,
    get_log_options,
    get_restart_options,
    get_monitor_menu,
    get_back_to_main_menu,
    get_back_to_monitor_menu,
    get_log_filter_options
)

__all__ = [
    'get_main_menu',
    'get_log_options',
    'get_restart_options',
    'get_monitor_menu',
    'get_back_to_main_menu',
    'get_back_to_monitor_menu',
    'get_log_filter_options'
]

# Available keyboard menus documentation
"""
Available keyboard menus:

1. Main Menu (get_main_menu):
   - Primary navigation menu with all main options

2. Log Options (get_log_options):
   - Options for viewing different service logs

3. Restart Options (get_restart_options):
   - Options for restarting different services

4. Monitor Menu (get_monitor_menu):
   - Monitoring control options

5. Navigation Menus:
   - get_back_to_main_menu: Simple back to main menu button
   - get_back_to_monitor_menu: Back to monitor menu with main menu option

6. Log Filter Options (get_log_filter_options):
   - Log level filter options for a specific service

Usage example:
    from ..keyboards import get_main_menu
    
    async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = get_main_menu()
        await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
"""