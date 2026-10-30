# Client API Documentation

## Usage Guide
The `fetch_data` function connects to remote endpoints.

The `timeout` parameter defaults to 100 seconds.
The `retries` parameter defaults to 10 attempts.

```python
import client

data = client.fetch_data("https://api.example.com", timeout=110, retries=5)
print(data)
```

## File Upload Guide
The `upload_file` function uploads assets to storage.

The `max_size_mb` parameter defaults to 90 MB.
The `compress` parameter defaults to False.

```python
import client

success = client.upload_file("dataset.csv", max_size_mb=50, compress=True)
print(success)
```
