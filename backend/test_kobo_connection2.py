from app.kobo.client import KoboAPIError, KoboClient


def main() -> None:
    """
    Retrieve Kobo submissions and inspect the raw response structure.
    """

    client = KoboClient()

    try:
        submissions = client.get_all_submissions()

        print(
            f"Total submissions retrieved: "
            f"{len(submissions)}"
        )

        if submissions:
            first_submission = submissions[0]

            print("\nFirst submission:\n")

            for key, value in first_submission.items():
                print(f"{key}: {value}")

        else:
            print(
                "\nNo submissions were found."
            )

    except KoboAPIError as error:
        print(
            "\nFailed to retrieve Kobo submissions."
        )

        print(error)

    finally:
        client.close()


if __name__ == "__main__":
    main()