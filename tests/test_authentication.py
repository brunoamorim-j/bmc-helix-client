
import pytest
from unittest.mock import Mock, patch

from bmc_helix_client import HelixClient, HelixClientError


def test_authenticate_success():
    client = HelixClient(
        base_url="https://helix.example.com",
        username="test_user",
        password="test_password"
    )

    # Simula a resposta da API
    mock_response = Mock()
    mock_response.text = "fake-jwt-token"

    # Simula uma resposta HTTP sem erros
    mock_response.raise_for_status.return_value = None

    with patch("bmc_helix_client.client.req.post") as mock_post:
        mock_post.return_value = mock_response

        client.authenticate()

    assert client.jwt_token == "fake-jwt-token"

    mock_post.assert_called_once_with(
        "https://helix.example.com/api/jwt/login",
        data={
            "username": "test_user",
            "password": "test_password"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=60,
        verify=True
    )


def test_authenticate_empty_token():
    client = HelixClient(
        base_url="https://helix.example.com",
        username="test_user",
        password="test_password"
    )

    mock_response = Mock()
    mock_response.text = ""
    mock_response.raise_for_status.return_value = None

    with patch("bmc_helix_client.client.req.post") as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(HelixClientError):
            client.authenticate()


def test_authenticate_timeout():
    from requests.exceptions import Timeout

    client = HelixClient(
        base_url="https://helix.example.com",
        username="test_user",
        password="test_password"
    )

    with patch("bmc_helix_client.client.req.post") as mock_post:
        mock_post.side_effect = Timeout("Connection timed out")

        with pytest.raises(HelixClientError):
            client.authenticate()
