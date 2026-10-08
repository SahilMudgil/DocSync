# Client API Documentation

## Usage Guide
The `fetch_data` function connects to remote endpoints.

The `timeout` parameter defaults to 30 seconds.

```python
import client

data = client.fetch_data("https://api.example.com", timeout=30)
print(data)
```
