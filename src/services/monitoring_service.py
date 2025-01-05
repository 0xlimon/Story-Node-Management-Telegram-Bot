"""Monitoring service for the Story Validator Bot."""

import logging
from typing import Dict, Any, Optional
from telegram import Bot
from telegram.ext import ContextTypes
from aiohttp.client_exceptions import ClientConnectorError

from . import system_service
from .sync_service import SyncMonitor
from ..utils.helpers import split_message

logger = logging.getLogger(__name__)

class MonitoringService:
    """Handles monitoring operations."""
    
    @staticmethod
    async def send_monitoring_update(context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send monitoring update to the specified chat."""
        chat_id = context.job.chat_id
        if not context.chat_data.get('monitoring', False):
            return

        logger.info(f"Sending monitoring update to chat {chat_id}")
        try:
            # Get service statuses
            service_statuses = system_service.check_services_status()
            
            # Get disk usage
            disk = system_service.get_system_info()['disk_percent']
            message = "📝 <b>Monitoring Update:</b>\n\n"
            
            # Add disk usage information
            message += "💾 <b>Disk Status:</b>\n"
            message += f"• Usage: {disk}%\n"
            if disk > 90:
                message += "⚠️ <b>Warning:</b> Disk usage is very high!\n"
            elif disk > 80:
                message += "⚠️ <b>Note:</b> Disk usage is getting high\n"
            message += "\n"
            
            # Add service status information
            message += "🔧 <b>Service Status:</b>\n"
            for service, status in service_statuses.items():
                if status == "active":
                    icon = "✅"
                    status_text = "Running"
                elif status == "inactive":
                    icon = "⚫"
                    status_text = "Stopped"
                elif status == "failed":
                    icon = "❌"
                    status_text = "Failed"
                elif status == "stopped":
                    icon = "⏹️"
                    status_text = "Stopped"
                elif status == "unknown":
                    icon = "❓"
                    status_text = "Status Unknown"
                else:
                    icon = "⚠️"
                    status_text = f"Status: {status}"
                
                message += f"• {service}: {icon} {status_text}\n"
            message += "\n"
            
            try:
                # Get advanced sync status
                sync_monitor = SyncMonitor()
                sync_metrics, is_healthy = await sync_monitor.get_sync_status()
                
                # Add sync status information
                message += "🔄 <b>Synchronization Status:</b>\n"
                message += f"• Current Height: <code>{sync_metrics['current_height']}</code>\n"
                message += f"• Network Height: <code>{sync_metrics['network_height']}</code>\n"
                message += f"• Blocks Behind: <code>{sync_metrics['blocks_behind']}</code>\n"
                message += f"• Sync Progress: <code>{sync_metrics['sync_percent']:.2f}%</code>\n"
                
                if sync_metrics['blocks_behind'] > 0 and sync_metrics['time_remaining']:
                    message += f"• Est. Time Remaining: {sync_metrics['time_remaining']}\n"
                
                # Add health status and warnings
                if sync_metrics['blocks_behind'] > 100:
                    message += "⚠️ Node is significantly behind the network\n"
                if sync_metrics['catching_up']:
                    message += "⚠️ Node is still catching up with the network\n"
            except ClientConnectorError as e:
                message += (
                    "🚫 <b>Node Connection Error:</b>\n\n"
                    "Cannot connect to the node API.\n"
                    "<b>Possible reasons:</b>\n"
                    "• The node service is not running\n"
                    "• The node's API port (26657) is not accessible\n"
                    "• The node is experiencing issues\n\n"
                    "<b>Suggested actions:</b>\n"
                    "1. Check if the node service is running\n"
                    "2. Verify the API port is accessible\n"
                    "3. Check node logs for potential issues\n"
                    f"\n<i>Technical details:</i> {str(e)}"
                )
            except Exception as e:
                message += (
                    "❌ <b>Error Checking Node Status:</b>\n\n"
                    f"<code>{str(e)}</code>\n\n"
                    "The monitoring service will continue running.\n"
                    "Please check your node's status manually."
                )
            
            # Split message if needed and send
            if len(message) <= 4096:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                logger.info(f"Monitoring update sent successfully to chat {chat_id}")
            else:
                logger.info(f"Splitting long monitoring update for chat {chat_id}")
                messages = split_message(message)
                for msg in messages:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=msg,
                        parse_mode='HTML'
                    )

        except Exception as e:
            error_message = (
                "❌ <b>Monitoring Update Error:</b>\n\n"
                f"<code>{str(e)}</code>\n\n"
                "The monitoring service will continue running.\n"
                "If this error persists, please check your node's configuration."
            )
            logger.error(f"Error in monitoring update: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=error_message,
                parse_mode='HTML'
            )

    @staticmethod
    def get_monitoring_status(chat_data: Dict[str, Any], interval: int) -> Dict[str, Any]:
        """Get current monitoring status."""
        monitoring_active = chat_data.get('monitoring', False)
        return {
            'active': monitoring_active,
            'interval_minutes': interval // 60,
            'status': '✅ Yes' if monitoring_active else '❌ No'
        }

    @staticmethod
    def activate_monitoring(
        chat_data: Dict[str, Any],
        job_queue: Any,
        chat_id: int,
        interval: int
    ) -> bool:
        """Activate monitoring for a chat."""
        if chat_data.get('monitoring', False):
            logger.info(f"Monitoring already active for chat {chat_id}")
            return False
            
        chat_data['monitoring'] = True
        logger.info(f"Monitoring activated for chat {chat_id}")
        job_queue.run_repeating(
            MonitoringService.send_monitoring_update,
            interval=interval,
            first=10,
            chat_id=chat_id,
            name=f"monitor_{chat_id}"
        )
        return True

    @staticmethod
    def deactivate_monitoring(
        chat_data: Dict[str, Any],
        job_queue: Any,
        chat_id: int
    ) -> bool:
        """Deactivate monitoring for a chat."""
        if not chat_data.get('monitoring', False):
            logger.info(f"Monitoring already inactive for chat {chat_id}")
            return False
            
        chat_data['monitoring'] = False
        logger.info(f"Monitoring deactivated for chat {chat_id}")
        current_jobs = job_queue.get_jobs_by_name(f"monitor_{chat_id}")
        for job in current_jobs:
            job.schedule_removal()
        return True