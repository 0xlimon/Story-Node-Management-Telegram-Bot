"""Service module for system-related operations."""

import logging
import psutil
import socket
import subprocess
from typing import Dict, Any, Tuple

from ..utils.config import STORY_SERVICE, STORY_GETH_SERVICE

logger = logging.getLogger(__name__)

def get_service_status(service_name: str) -> str:
    """
    Get the status of a systemd service.
    
    Args:
        service_name: Name of the service to check
        
    Returns:
        Current status of the service
    """
    try:
        # Use systemctl is-active for basic status
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        status = result.stdout.strip()
        
        if status == "active":
            return "active"
            
        # If not active, get more detailed status
        result = subprocess.run(
            ["systemctl", "status", service_name],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check for common inactive states
        if "inactive" in result.stdout:
            return "inactive"
        elif "failed" in result.stdout:
            return "failed"
        elif "dead" in result.stdout:
            return "stopped"
        else:
            return status
            
    except Exception as e:
        logger.error(f"Error checking service {service_name} status: {e}")
        return "unknown"

def check_services_status() -> Dict[str, str]:
    """
    Check the status of story and story-geth services.
    
    Returns:
        Dictionary containing service statuses
    """
    return {
        STORY_SERVICE: get_service_status(STORY_SERVICE),
        STORY_GETH_SERVICE: get_service_status(STORY_GETH_SERVICE)
    }

def get_system_info() -> Dict[str, float]:
    """
    Get basic system information including CPU, memory, and disk usage.
    
    Returns:
        Dictionary containing system metrics
    """
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }

def get_detailed_performance_metrics() -> Dict[str, Any]:
    """
    Get detailed performance metrics of the system.
    
    Returns:
        Dictionary containing detailed performance metrics
    """
    cpu_times = psutil.cpu_times_percent()
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk_io = psutil.disk_io_counters()
    disk_usage = psutil.disk_usage('/')
    cpu_freq = psutil.cpu_freq()
    load_avg = psutil.getloadavg()
    
    return {
        'cpu': {
            'user': cpu_times.user,
            'system': cpu_times.system,
            'idle': cpu_times.idle,
            'frequency': cpu_freq.current,
            'load_average': load_avg
        },
        'memory': {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'buffers': memory.buffers,
            'cached': memory.cached
        },
        'swap': {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent
        },
        'disk': {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent': disk_usage.percent,
            'io': {
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes,
                'read_count': disk_io.read_count,
                'write_count': disk_io.write_count
            }
        }
    }

def get_network_stats() -> Dict[str, Any]:
    """
    Get detailed network statistics.
    
    Returns:
        Dictionary containing network statistics
    """
    net_io = psutil.net_io_counters()
    net_connections = psutil.net_connections()
    net_if_addrs = psutil.net_if_addrs()
    
    interfaces = {}
    for interface, addrs in net_if_addrs.items():
        interfaces[interface] = {
            'addresses': [
                {
                    'address': addr.address,
                    'family': 'IPv4' if addr.family == socket.AF_INET else 'IPv6'
                }
                for addr in addrs
                if addr.family in (socket.AF_INET, socket.AF_INET6)
            ]
        }
    
    return {
        'io': {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        },
        'connections_count': len(net_connections),
        'interfaces': interfaces
    }

def restart_service(service_name: str) -> Tuple[bool, str]:
    """
    Restart a system service.
    
    Args:
        service_name: Name of the service to restart
        
    Returns:
        Tuple of (success, message)
    """
    try:
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        return True, f"✅ {service_name} service restarted successfully."
    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Error restarting {service_name} service: {str(e)}"
        logger.error(error_msg)
        return False, error_msg