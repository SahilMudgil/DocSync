# Client API Documentation

## Usage Guide
The `fetch_data` function connects to remote endpoints.

The `timeout` parameter defaults to 70 seconds.
The `retries` parameter defaults to 15 attempts.

```python
import client

data = client.fetch_data("https://api.example.com", timeout=110, retries=5)
print(data)
```

## File Upload Guide
The `upload_file` function uploads assets to storage.

The `max_size_mb` parameter defaults to 40 MB.
The `compress` parameter defaults to True.

```python
import client

success = client.upload_file("dataset.csv", max_size_mb=50, compress=True)
print(success)
```
