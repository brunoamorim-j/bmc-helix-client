import pytest

from bmc_helix_client import HelixClient, HelixClientError

def test_client_initialization_success():
    client = HelixClient(
        base_url="https://helix.example.com/",
        username="test_user",
        password="test_password"
    )
    
    assert client.base_url == "https://helix.example.com"
    assert client.username == "test_user"
    assert client.password == "test_password"
    assert client.timeout == 60
    assert client.verify_ssl is True
    assert client.jwt_token is None



@pytest.mark.parametrize(
    "parameter, value",
    [
        ("base_url", ""),
        ("username", ""),
        ("password", "")
        
    ]
)

def test_client_initialization_rejects_empty_parameters(parameter, value):
    parameters = {
        "base_url": "https://helix.example.com",
        "username": "test_user",
        "password": "test_password"
    }
    
    parameters[parameter] = value
    
    with pytest.raises(HelixClientError):
        HelixClient(**parameters)
    
@pytest.mark.parametrize("timeout", [0, -1])
def test_client_initialization_rejects_invalid_timeout(timeout):
    with pytest.raises(HelixClientError):
        HelixClient(
            base_url="https://helix.example.com",
            username="test_user",
            password="test_password",
            timeout=timeout
        )