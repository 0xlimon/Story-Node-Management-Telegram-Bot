"""Story Validator Bot - A Telegram bot for monitoring Story nodes."""

from .main import main, create_application
from .decorators import admin_only

__version__ = "1.0.0"
__author__ = "Story Validator Bot Team"
__description__ = "A Telegram bot for monitoring and managing Story nodes"

__all__ = [
    'main',
    'create_application',
    'admin_only'
]

# Bot capabilities documentation
"""
Story Validator Bot Capabilities:

1. Node Monitoring:
   - Status checking
   - Block height monitoring
   - Synchronization status
   - Validator information

2. System Management:
   - Service control (start/stop/restart)
   - Log viewing and filtering
   - Performance metrics
   - Network statistics

3. Continuous Monitoring:
   - Automated status updates
   - Configurable monitoring intervals
   - Alert notifications

4. Security:
   - Admin-only access
   - Secure command handling
   - Protected operations

5. Backup:
   - Validator state backup
   - Secure file transfer
"""