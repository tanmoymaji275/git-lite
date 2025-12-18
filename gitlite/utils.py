import os
import time
 
def get_signature():
    """Returns a standard Git signature string: 'Name <email> timestamp timezone'"""
    name = os.environ.get("GIT_AUTHOR_NAME", "Anonymous")
    email = os.environ.get("GIT_AUTHOR_EMAIL", "anonymous@example.com")
    
    timestamp = int(time.time())
    offset = -time.timezone if (time.localtime().tm_isdst == 0) else -time.altzone
    offset_hours = offset // 3600
    offset_minutes = (offset % 3600) // 60
    timezone = f"{offset_hours:+03d}{offset_minutes:02d}"
    
    return f"{name} <{email}> {timestamp} {timezone}"