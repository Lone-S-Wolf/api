
from datetime import datetime, timezone
import json
from typing import Any

def normalize_to_utc(dt: datetime) -> datetime:
    """
    Convert any datetime to UTC.
    
    Args:
        dt (datetime): Input datetime object
    
    Returns:
        datetime: UTC normalized datetime
    """
    if dt is None:
        return None
    
    # If datetime is naive, assume it's in local time and convert to UTC
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    
    # If datetime has timezone info, convert to UTC
    return dt.astimezone(timezone.utc)

def localize_datetime(dt: datetime, local_tz=timezone.utc):
    """
    Convert UTC datetime to specific timezone.
    
    Args:
        dt (datetime): UTC datetime to convert
        local_tz (timezone, optional): Target timezone. Defaults to UTC.
    
    Returns:
        datetime: Localized datetime
    """
    if dt is None:
        return None
    
    # Ensure input is in UTC
    utc_dt = normalize_to_utc(dt)
    
    # Convert to specified timezone
    return utc_dt.astimezone(local_tz)

def json_serializer(obj: Any) -> str:
    """
    Custom JSON serializer to handle datetime objects.
    
    Args:
        obj (Any): Object to serialize
    
    Returns:
        str: JSON serialized string
    """
    if isinstance(obj, datetime):
        # Always serialize in UTC
        return normalize_to_utc(obj).isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def json_deserializer(json_str: str) -> Any:
    """
    Custom JSON deserializer to parse datetime objects.
    
    Args:
        json_str (str): JSON string to deserialize
    
    Returns:
        Any: Deserialized object
    """
    def datetime_parser(json_dict):
        for key, value in json_dict.items():
            if isinstance(value, str):
                try:
                    # Try to parse datetime
                    json_dict[key] = datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    pass
        return json_dict
    
    return json.loads(json_str, object_hook=datetime_parser)