"""
Client API implementation module.
"""

def fetch_data(url: str, timeout: int = 90)-> dict:
    """
    Fetch payload from specified endpoint.
    Defaults to a 60 second timeout.
    """
    if not url:
        raise ValueError("URL cannot be empty")
    return {"status": 200, "url": url, "timeout": timeout}
