
import os

from bmc_helix_client import HelixClient, HelixClientError


def main():
    base_url = os.getenv("HELIX_BASE_URL")
    username = os.getenv("HELIX_USERNAME")
    password = os.getenv("HELIX_PASSWORD")

    if not all([base_url, username, password]):
        raise ValueError("Configure HELIX_BASE_URL, HELIX_USERNAME and HELIX_PASSWORD.")

    try:
        client = HelixClient(
            base_url=base_url,
            username=username,
            password=password,
            verify_ssl=False
        )

        print("Client created successfully.")

        client.authenticate()

        if not client.jwt_token:
            raise HelixClientError("Authentication returned an empty token.")

        print("Authentication successful.")
        print("JWT token received and stored internally.")

    except HelixClientError as error:
        print(f"Helix error: {error}")
        raise


if __name__ == "__main__":
    main()
