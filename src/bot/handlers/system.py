"""Handler module for system-related commands and callbacks."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from ...services import (
    get_system_info,
    get_detailed_performance_metrics,
    get_network_stats
)
from ..decorators import admin_only
from ..keyboards.menus import get_back_to_main_menu

logger = logging.getLogger(__name__)

def format_size(size_bytes: int) -> str:
    """
    Format byte size to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string with appropriate unit
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

@admin_only
async def system_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show basic system information.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        system_data = get_system_info()
        
        message = "💻 System Information:\n\n"
        message += f"CPU Usage: {system_data['cpu_percent']}%\n"
        message += f"Memory Usage: {system_data['memory_percent']}%\n"
        message += f"Disk Usage: {system_data['disk_percent']}%\n"
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=get_back_to_main_menu()
        )
        
    except Exception as e:
        error_msg = f"❌ Error fetching system information: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_main_menu()
        )

@admin_only
async def performance_metrics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show detailed performance metrics.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        metrics = get_detailed_performance_metrics()
        
        message = "📈 Detailed Performance Metrics:\n\n"
        
        # CPU section
        message += "CPU Usage:\n"
        message += f"  User: {metrics['cpu']['user']}%\n"
        message += f"  System: {metrics['cpu']['system']}%\n"
        message += f"  Idle: {metrics['cpu']['idle']}%\n"
        message += f"  Current Frequency: {metrics['cpu']['frequency']:.2f} MHz\n"
        message += f"  Load Average: {metrics['cpu']['load_average'][0]:.2f}, "
        message += f"{metrics['cpu']['load_average'][1]:.2f}, "
        message += f"{metrics['cpu']['load_average'][2]:.2f}\n\n"
        
        # Memory section
        message += "Memory Usage:\n"
        message += f"  Total: {format_size(metrics['memory']['total'])}\n"
        message += f"  Available: {format_size(metrics['memory']['available'])}\n"
        message += f"  Used: {format_size(metrics['memory']['used'])} ({metrics['memory']['percent']}%)\n"
        message += f"  Buffers: {format_size(metrics['memory']['buffers'])}\n"
        message += f"  Cached: {format_size(metrics['memory']['cached'])}\n\n"
        
        # Swap section
        message += "Swap Usage:\n"
        message += f"  Total: {format_size(metrics['swap']['total'])}\n"
        message += f"  Used: {format_size(metrics['swap']['used'])} ({metrics['swap']['percent']}%)\n"
        message += f"  Free: {format_size(metrics['swap']['free'])}\n\n"
        
        # Disk section
        message += "Disk Usage:\n"
        message += f"  Total: {format_size(metrics['disk']['total'])}\n"
        message += f"  Used: {format_size(metrics['disk']['used'])} ({metrics['disk']['percent']}%)\n"
        message += f"  Free: {format_size(metrics['disk']['free'])}\n\n"
        
        message += "Disk I/O (since boot):\n"
        message += f"  Read: {format_size(metrics['disk']['io']['read_bytes'])}\n"
        message += f"  Write: {format_size(metrics['disk']['io']['write_bytes'])}\n"
        message += f"  Read Count: {metrics['disk']['io']['read_count']}\n"
        message += f"  Write Count: {metrics['disk']['io']['write_count']}\n"
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=get_back_to_main_menu()
        )
        
    except Exception as e:
        error_msg = f"❌ Error fetching performance metrics: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_main_menu()
        )

@admin_only
async def network_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show network statistics.
    
    Args:
        update: The update object
        context: The context object
    """
    try:
        stats = get_network_stats()
        
        message = "🌐 Network Statistics:\n\n"
        
        # Network I/O section
        message += "Network I/O (since boot):\n"
        message += f"  Bytes Sent: {format_size(stats['io']['bytes_sent'])}\n"
        message += f"  Bytes Received: {format_size(stats['io']['bytes_recv'])}\n"
        message += f"  Packets Sent: {stats['io']['packets_sent']}\n"
        message += f"  Packets Received: {stats['io']['packets_recv']}\n"
        message += f"  Errors In: {stats['io']['errin']}\n"
        message += f"  Errors Out: {stats['io']['errout']}\n"
        message += f"  Drop In: {stats['io']['dropin']}\n"
        message += f"  Drop Out: {stats['io']['dropout']}\n\n"
        
        # Connections section
        message += f"Active Connections: {stats['connections_count']}\n\n"
        
        # Network interfaces section
        message += "Network Interfaces:\n"
        for interface, data in stats['interfaces'].items():
            message += f"  {interface}:\n"
            for addr in data['addresses']:
                message += f"    {addr['family']} Address: {addr['address']}\n"
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=get_back_to_main_menu()
        )
        
    except Exception as e:
        error_msg = f"❌ Error fetching network statistics: {str(e)}"
        logger.error(error_msg)
        await update.callback_query.edit_message_text(
            error_msg,
            reply_markup=get_back_to_main_menu()
        )