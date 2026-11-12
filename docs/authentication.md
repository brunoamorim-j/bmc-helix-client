

# Authentication

BMC Helix Client uses JWT (JSON Web Token) authentication to communicate with the BMC Helix ITSM REST API.

## Creating the Client

Import `HelixClient` and provide your Helix instance URL and credentials.

```python
from bmc_helix_client import HelixClient
import os

client = HelixClient(
    base_url=os.getenv("HELIX_BASE_URL"),
    username=os.getenv("HELIX_USERNAME"),
    password=os.getenv("HELIX_PASSWORD")
)
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `base_url` | `str` | Required | Base URL of the BMC Helix instance. |
| `username` | `str` | Required | BMC Helix username. |
| `password` | `str` | Required | BMC Helix password. |
| `timeout` | `int` | `60` | HTTP request timeout in seconds. |
| `verify_ssl` | `bool` | `True` | Enables or disables SSL certificate verification. |

## Authenticating

Call `authenticate()` to obtain a JWT token.

```python
client.authenticate()
```

The client stores the JWT token internally and uses it to authenticate subsequent API requests.

Authentication must be performed before calling methods that interact with the Helix API.

## Complete Example

```python
from bmc_helix_client import HelixClient
import os

client = HelixClient(
    base_url=os.getenv("HELIX_BASE_URL"),
    username=os.getenv("HELIX_USERNAME"),
    password=os.getenv("HELIX_PASSWORD")
)

client.authenticate()

incidents = client.search_incident(
    search_criteria={"Status": "open"}
)

print(incidents)
```

## SSL Certificate Verification

SSL certificate verification is enabled by default (`verify_ssl=True`).

If your Helix environment uses an internal or self-signed certificate authority that is not trusted by your system, authentication may fail with an SSL certificate verification error.

For testing in controlled environments, you can disable certificate verification:

```python
client = HelixClient(
    base_url="https://your-helix-instance",
    username="your_username",
    password="your_password",
    verify_ssl=False
)
```

**Security warning:** Disabling SSL certificate verification is not recommended for production environments because it removes protection against certificate impersonation.

For production environments, configure your system to trust the appropriate certificate authority and keep `verify_ssl=True`.

## Security Recommendations

- Avoid hardcoding credentials in source code.
- Use environment variables or a secure secrets manager.
- Never commit passwords or authentication tokens to version control.
- Keep SSL verification enabled whenever possible.
