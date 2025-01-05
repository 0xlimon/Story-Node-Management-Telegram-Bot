"""Helper functions for the Story Validator Bot."""

from typing import Any, List


def safe_get(data: dict, *keys: str, default: Any = "Not available") -> Any:
    """
    Safely get nested dictionary values.
    
    Args:
        data: The dictionary to search in
        *keys: The keys to search for
        default: The default value to return if the key is not found
        
    Returns:
        The value if found, otherwise the default value
    """
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return default
    return data


def split_message(message: str, max_length: int = 4000) -> List[str]:
    """
    Split a message into multiple parts if it exceeds the maximum length.
    
    Args:
        message: The message to split
        max_length: The maximum length of each part
        
    Returns:
        A list of message parts
    """
    parts = []
    while len(message) > max_length:
        split_index = message.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(message[:split_index])
        message = message[split_index:]
    parts.append(message)
    return parts