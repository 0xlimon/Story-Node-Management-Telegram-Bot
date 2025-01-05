"""Keyboard menu definitions for the Telegram bot."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu() -> InlineKeyboardMarkup:
    """Get the main menu keyboard markup."""
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("📜 Logs", callback_data="logs"),
         InlineKeyboardButton("🔄 Restart Services", callback_data="restart")],
        [InlineKeyboardButton("💻 System Info", callback_data="system_info"),
         InlineKeyboardButton("📝 Monitor", callback_data="monitor")],
        [InlineKeyboardButton("📈 Performance", callback_data="performance"),
         InlineKeyboardButton("🌐 Network", callback_data="network")],
        [InlineKeyboardButton("✅ Validator", callback_data="validator"),
         InlineKeyboardButton("❔ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_log_options() -> InlineKeyboardMarkup:
    """Get the log options keyboard markup."""
    keyboard = [
        [InlineKeyboardButton("Story Logs", callback_data="logs_story"),
         InlineKeyboardButton("Story-Geth Logs", callback_data="logs_story-geth")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_restart_options() -> InlineKeyboardMarkup:
    """Get the restart options keyboard markup."""
    keyboard = [
        [InlineKeyboardButton("Restart Story", callback_data="restart_story"),
         InlineKeyboardButton("Restart Story-Geth", callback_data="restart_story-geth")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_monitor_menu() -> InlineKeyboardMarkup:
    """Get the monitor menu keyboard markup."""
    keyboard = [
        [InlineKeyboardButton("✅ Activate Monitoring", callback_data="monitor_activate")],
        [InlineKeyboardButton("❌ Deactivate Monitoring", callback_data="monitor_deactivate")],
        [InlineKeyboardButton("📋 View Monitoring Status", callback_data="monitor_status")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_main_menu() -> InlineKeyboardMarkup:
    """Get a simple back to main menu keyboard markup."""
    keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="start")]]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_monitor_menu() -> InlineKeyboardMarkup:
    """Get a keyboard markup with back to monitor menu and main menu options."""
    keyboard = [
        [InlineKeyboardButton("⬅️ Back to Monitor Menu", callback_data="monitor")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_log_filter_options(service: str) -> InlineKeyboardMarkup:
    """Get the log filter options keyboard markup."""
    keyboard = [
        [InlineKeyboardButton("All Levels", callback_data=f"log_filter_{service}_all")],
        [InlineKeyboardButton("ERROR", callback_data=f"log_filter_{service}_ERROR")],
        [InlineKeyboardButton("WARNING", callback_data=f"log_filter_{service}_WARNING")],
        [InlineKeyboardButton("INFO", callback_data=f"log_filter_{service}_INFO")],
        [InlineKeyboardButton("⬅️ Back to Logs Menu", callback_data="logs")],
        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)