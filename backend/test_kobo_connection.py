from app.kobo.client import KoboAPIError, KoboClient


def main() -> None:
    """
    Test the connection to KoboToolbox and inspect the configured asset.
    """

    client = KoboClient()

    try:
        asset = client.get_asset()

        print("Successfully connected to KoboToolbox.\n")

        print(f"Asset UID: {asset.uid}")
        print(f"Asset Name: {asset.name}")
        print(f"Data Endpoint: {asset.data}")

    except KoboAPIError as error:
        print("\nKobo API connection failed.")
        print(error)

    finally:
        client.close()


if __name__ == "__main__":
    main()