"""Handlers package for the Story Validator Bot."""

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from .start import handle_start
from .status import handle_status
from .help import handle_help
from .restart import show_restart_options, handle_restart_service
from .monitoring import (
    show_monitor_menu,
    activate_monitoring,
    deactivate_monitoring,
    view_monitoring_status
)
from .logs import (
    show_log_options,
    show_log_filter_options,
    handle_log_filter,
    view_logs
)
from .system import (
    system_info,
    performance_metrics,
    network_stats
)
from .validator import validator_info

# Dictionary mapping callback data to handler functions
callback_handlers = {
    # Navigation handlers
    "start": handle_start,  # Show main menu
    "help": handle_help,    # Show help message
    
    # Main menu handlers
    "status": handle_status,
    "system_info": system_info,
    "performance": performance_metrics,
    "network": network_stats,
    "validator": validator_info,
    
    # Restart handlers
    "restart": show_restart_options,
    "restart_story": lambda u, c: handle_restart_service(u, c, "story"),
    "restart_story-geth": lambda u, c: handle_restart_service(u, c, "story-geth"),
    
    # Monitoring handlers
    "monitor": show_monitor_menu,
    "monitor_activate": activate_monitoring,
    "monitor_deactivate": deactivate_monitoring,
    "monitor_status": view_monitoring_status,
    
    # Log handlers
    "logs": show_log_options,
    "logs_story": lambda u, c: view_logs(u, c, "story"),
    "logs_story-geth": lambda u, c: view_logs(u, c, "story-geth"),
    "log_filter": handle_log_filter
}

# Command handlers mapping
command_handlers = {
    "start": handle_start,  # Using dedicated start handler
    "help": handle_help    # Add help command handler
}

__all__ = [
    # Main handlers
    'handle_start',
    'handle_status',
    'handle_help',
    'system_info',
    'performance_metrics',
    'network_stats',
    'validator_info',
    
    # Restart handlers
    'show_restart_options',
    'handle_restart_service',
    
    # Monitoring handlers
    'show_monitor_menu',
    'activate_monitoring',
    'deactivate_monitoring',
    'view_monitoring_status',
    
    # Log handlers
    'show_log_options',
    'show_log_filter_options',
    'handle_log_filter',
    'view_logs',
    
    # Handler mappings
    'callback_handlers',
    'command_handlers'
]