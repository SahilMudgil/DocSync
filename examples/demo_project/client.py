"""
Client API implementation module.
"""

def fetch_data(url: str, timeout: int = 50, retries: int = 5) -> dict:
    """
    Fetch payload from specified endpoint.
    Defaults to a 100 second timeout.
    The retries parameter defaults to 10 attempts.
    """
    if not url:
        raise ValueError("URL cannot be empty")
    return {"status": 200, "url": url, "timeout": timeout, "retries": retries}


def upload_file(filepath: str, max_size_mb: int = 90, compress: bool = False) -> bool:
    """
    Upload file asset to remote storage.
    The max_size_mb parameter defaults to 90 MB.
    The compress parameter defaults to False.
    """
    if not filepath:
        raise ValueError("Filepath cannot be empty")
    return True
