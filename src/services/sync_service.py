"""Service module for sync monitoring."""

import logging
import asyncio
import aiohttp
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta

from ..utils.config import SERVER_PORT, RPC_ENDPOINT_1, RPC_ENDPOINT_2

logger = logging.getLogger(__name__)

class SyncMonitor:
    """Monitor node synchronization status."""
    
    def __init__(self):
        self.last_height = 0
        self.last_check_time = None
        self.sync_speed = 0  # blocks per second
        
    async def get_network_height(self) -> int:
        """
        Get the current network height from RPC endpoints.
        
        Returns:
            Current network block height
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RPC_ENDPOINT_1) as response:
                    if response.status == 200:
                        data = await response.json()
                        return int(data['result']['sync_info']['latest_block_height'])
        except Exception as e:
            logger.warning(f"Failed to get height from RPC1: {e}")
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RPC_ENDPOINT_2) as response:
                    if response.status == 200:
                        data = await response.json()
                        return int(data['result']['sync_info']['latest_block_height'])
        except Exception as e:
            logger.warning(f"Failed to get height from RPC2: {e}")
            
        raise Exception("Failed to get network height from any RPC endpoint")

    async def get_node_status(self) -> Dict[str, Any]:
        """
        Get detailed node status.
        
        Returns:
            Dictionary containing node status information
        """
        node_rpc_url = f"http://localhost:{SERVER_PORT}/status"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{node_rpc_url}") as response:
                if response.status != 200:
                    raise Exception(f"Failed to get node status: HTTP {response.status}")
                return await response.json()

    def calculate_sync_metrics(
        self,
        current_height: int,
        network_height: int,
        node_status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate sync progress and related metrics.
        
        Args:
            current_height: Current node height
            network_height: Network height
            node_status: Node status information
            
        Returns:
            Dictionary containing sync metrics
        """
        now = datetime.now()
        
        # Calculate sync progress
        blocks_behind = network_height - current_height
        if blocks_behind > 0:
            # Use a more accurate progress calculation
            sync_percent = ((current_height / network_height) * 100) if network_height > 0 else 0
            # Round to 2 decimal places and ensure it's not 100% if behind
            sync_percent = min(99.99, round(sync_percent, 2))
        else:
            sync_percent = 100
            blocks_behind = 0
            
        # Calculate sync speed
        if self.last_height > 0 and self.last_check_time:
            time_diff = (now - self.last_check_time).total_seconds()
            if time_diff > 0:
                height_diff = current_height - self.last_height
                self.sync_speed = height_diff / time_diff
                
        # Update last values
        self.last_height = current_height
        self.last_check_time = now
        
        # Calculate estimated time remaining
        time_remaining = None
        if self.sync_speed > 0 and blocks_behind > 0:
            seconds_remaining = blocks_behind / self.sync_speed
            time_remaining = str(timedelta(seconds=int(seconds_remaining)))
            
        return {
            'current_height': current_height,
            'network_height': network_height,
            'blocks_behind': blocks_behind,
            'sync_percent': sync_percent,
            'sync_speed': self.sync_speed,
            'time_remaining': time_remaining,
            'catching_up': node_status['result']['sync_info']['catching_up']
        }

    async def get_sync_status(self) -> Tuple[Dict[str, Any], bool]:
        """
        Get comprehensive sync status.
        
        Returns:
            Tuple of (status_info, is_healthy)
        """
        try:
            # Get network height
            network_height = await self.get_network_height()
            
            # Get node status
            node_status = await self.get_node_status()
            current_height = int(node_status['result']['sync_info']['latest_block_height'])
            
            # Calculate metrics
            metrics = self.calculate_sync_metrics(current_height, network_height, node_status)
            
            # Determine health status
            is_healthy = (
                metrics['blocks_behind'] < 100 and  # Less than 100 blocks behind
                not metrics['catching_up']          # Not in catching up state
            )
            
            return metrics, is_healthy
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            raise