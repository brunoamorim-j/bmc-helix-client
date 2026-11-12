
import os

from bmc_helix_client import HelixClient, HelixClientError


def main():
    client = HelixClient(
        base_url=os.environ["HELIX_BASE_URL"],
        username=os.environ["HELIX_USERNAME"],
        password=os.environ["HELIX_PASSWORD"],
        verify_ssl=False
    )

    try:
        client.authenticate()

        results = client.search_ci(
            search_criteria={"Name": "SERVER_NAME"}
        )

        print("Authenticated request successful.")
        print(f"Records returned: {len(results)}")

    except HelixClientError as error:
        print(f"Helix error: {error}")
        raise


if __name__ == "__main__":
    main()
