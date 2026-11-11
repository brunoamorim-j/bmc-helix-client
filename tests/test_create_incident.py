import os

from bmc_helix_client import HelixClient, HelixClientError


def main():
    client = HelixClient(
        base_url=os.getenv("HELIX_BASE_URL"),
        username=os.environ["HELIX_USERNAME"],
        password=os.environ["HELIX_PASSWORD"],
        verify_ssl=False
    )

    try:
        client.authenticate()
        print("Autenticação realizada com sucesso!")

        incident_data = {
            "values": {
                "Login_ID": "your_username",
                "Description": "Incident summary",
                "Detailed_Decription": "Detailed incident description",
                "Reported Source": "Direct Input",
                "Service_Type": "User Service Restoration",
                "Categorization Tier 1": "Category 1",
                "Categorization Tier 2": "Category 2",
                "Categorization Tier 3": "Category 3",
                "Impact": "1-Extensive/Widespread",
                "Urgency": "3-Medium",
                "ServiceCI": "Business service name",
                "Assigned Support Company": "Support company",
                "Assigned Support Organization": "Support organization",
                "Assigned Group": "Support group",
                "Status": "Assigned"
            }
        }

        response = client.create_incident(incident_data)

        print("Incidente criado com sucesso!")
        print(f"Resposta: {response}")

    except HelixClientError as error:
        print(f"Erro ao criar incidente: {error}")


if __name__ == "__main__":
    main()
