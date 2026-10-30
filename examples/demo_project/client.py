"""
Client API implementation module.
"""

def fetch_data(url: str, timeout: int = 70, retries: int = 15) -> dict:
    """
    Fetch payload from specified endpoint.
    Defaults to a 50 second timeout.
    The retries parameter defaults to 5 attempts.
    """
    if not url:
        raise ValueError("URL cannot be empty")
    return {"status": 200, "url": url, "timeout": timeout, "retries": retries}


def upload_file(filepath: str, max_size_mb: int = 40, compress: bool = True) -> bool:
    """
    Upload file asset to remote storage.
    The max_size_mb parameter defaults to 40 MB.
    The compress parameter defaults to True.
    """
    if not filepath:
        raise ValueError("Filepath cannot be empty")
    return True
