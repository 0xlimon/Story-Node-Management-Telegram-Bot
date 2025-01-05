"""Service module for node-related operations."""

import logging
import aiohttp
from typing import Tuple, Dict, Any
from aiohttp.client_exceptions import ClientConnectorError

from ..utils.config import SERVER_PORT, RPC_ENDPOINT_1, RPC_ENDPOINT_2

logger = logging.getLogger(__name__)

def format_connection_error(error: Exception, endpoint: str) -> str:
    """
    Format connection error message to be more user-friendly.
    
    Args:
        error: The exception that occurred
        endpoint: The endpoint that failed
        
    Returns:
        A user-friendly error message
    """
    if isinstance(error, ClientConnectorError):
        return (
            f"🚫 Cannot connect to node at {endpoint}\n\n"
            "Possible reasons:\n"
            "• The node service is not running\n"
            "• The node's API port is not accessible\n"
            "• The node is experiencing issues\n\n"
            "Suggested actions:\n"
            "1. Check if the node service is running\n"
            "2. Verify the API port (26657) is accessible\n"
            "3. Check node logs for potential issues\n"
            f"\nTechnical details: {str(error)}"
        )
    return str(error)

async def fetch_latest_block(rpc_endpoint: str) -> int:
    """
    Fetch the latest block height from a given RPC endpoint.
    
    Args:
        rpc_endpoint: The RPC endpoint URL
        
    Returns:
        The latest block height
        
    Raises:
        Exception: With user-friendly message if the request fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rpc_endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    latest_block = int(data['result']['sync_info']['latest_block_height'])
                    return latest_block
                else:
                    raise Exception(
                        f"🚫 API request failed (Status {response.status})\n\n"
                        "The node's API responded with an error.\n"
                        "Please check if the node is functioning correctly."
                    )
    except ClientConnectorError as e:
        raise Exception(format_connection_error(e, rpc_endpoint))
    except Exception as e:
        raise Exception(f"🚫 Error fetching data: {str(e)}")

async def fetch_node_status() -> Dict[str, Any]:
    """
    Fetch the current node status.
    
    Returns:
        A dictionary containing node status information
        
    Raises:
        Exception: With user-friendly message if the request fails
    """
    node_rpc_url = f"http://localhost:{SERVER_PORT}/status"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(node_rpc_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(
                        f"🚫 Node API request failed (Status {response.status})\n\n"
                        "The local node's API responded with an error.\n"
                        "Please check if the node is functioning correctly."
                    )
    except ClientConnectorError as e:
        raise Exception(format_connection_error(e, node_rpc_url))
    except Exception as e:
        raise Exception(f"🚫 Error fetching node status: {str(e)}")

async def compare_block_heights() -> Tuple[str, bool]:
    """
    Compare the node's block height with the network's latest block height.
    
    Returns:
        A tuple containing (status_message, is_synced)
        
    Raises:
        Exception: With user-friendly message if comparison fails
    """
    try:
        try:
            latest_block_rpc1 = await fetch_latest_block(RPC_ENDPOINT_1)
            logger.info(f"Latest block from RPC_ENDPOINT_1: {latest_block_rpc1}")
        except Exception as e:
            logger.error(f"Error fetching from RPC_ENDPOINT_1: {e}")
            try:
                latest_block_rpc1 = await fetch_latest_block(RPC_ENDPOINT_2)
                logger.info(f"Latest block from RPC_ENDPOINT_2: {latest_block_rpc1}")
            except Exception as e2:
                raise Exception(
                    "🚫 Network Connection Error\n\n"
                    "Cannot connect to any RPC endpoints.\n"
                    "Please check your internet connection and try again.\n\n"
                    f"Technical details:\n"
                    f"RPC1 Error: {str(e)}\n"
                    f"RPC2 Error: {str(e2)}"
                )

        try:
            node_status = await fetch_node_status()
            node_block_height = int(node_status['result']['sync_info']['latest_block_height'])
            logger.info(f"Node's current block height: {node_block_height}")
        except Exception as e:
            raise Exception(
                "🚫 Local Node Error\n\n"
                "Cannot fetch local node status.\n"
                "Please check if your node is running and accessible.\n\n"
                f"Technical details: {str(e)}"
            )

        if node_block_height < latest_block_rpc1:
            difference = latest_block_rpc1 - node_block_height
            message = (
                f"🚨 **Block Synchronization Alert:**\n\n"
                f"Your node is behind by {difference} blocks.\n"
                f"Node Block Height: {node_block_height}\n"
                f"Network Latest Block: {latest_block_rpc1}\n\n"
                f"📝 Please check your node to ensure it's operating correctly."
            )
            return message, False
        else:
            message = (
                f"✅ **Block Synchronization Status:**\n\n"
                f"Your node is fully synchronized.\n"
                f"Node Block Height: {node_block_height}\n"
                f"Network Latest Block: {latest_block_rpc1}"
            )
            return message, True

    except Exception as e:
        logger.error(f"Error in compare_block_heights: {e}")
        return str(e), False

async def fetch_validator_info() -> Dict[str, Any]:
    """
    Fetch validator information from the node.
    
    Returns:
        A dictionary containing validator information
        
    Raises:
        Exception: With user-friendly message if the request fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            status_url = f'http://localhost:{SERVER_PORT}/status'
            validators_url = f'http://localhost:{SERVER_PORT}/validators'
            
            try:
                async with session.get(status_url) as resp:
                    status = await resp.json()
            except ClientConnectorError as e:
                raise Exception(format_connection_error(e, status_url))
            
            try:
                async with session.get(validators_url) as resp:
                    validators = await resp.json()
            except ClientConnectorError as e:
                raise Exception(format_connection_error(e, validators_url))
                
            return {
                'node_info': status['result']['node_info'],
                'sync_info': status['result']['sync_info'],
                'validator_info': status['result']['validator_info'],
                'validators': validators['result']
            }
    except Exception as e:
        if not isinstance(e, ClientConnectorError):
            raise Exception(
                "🚫 Validator Info Error\n\n"
                "Failed to fetch validator information.\n"
                "Please check if your node is running and accessible.\n\n"
                f"Technical details: {str(e)}"
            )