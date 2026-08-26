from typing import Any

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import settings
from app.schemas.kobo import KoboAsset, KoboSubmissionPage


class KoboAPIError(Exception):
    """
    Raised when the Kobo API request cannot be completed successfully.
    """

    pass


class KoboClient:
    """
    Client responsible for communicating with the KoboToolbox KPI v2 API.

    Responsibilities:
    - Authenticate using the Kobo API token.
    - Retrieve Kobo assets/projects.
    - Retrieve a specific asset.
    - Retrieve submission data.
    - Handle paginated submission responses.
    - Convert HTTP failures into application-specific exceptions.
    """

    def __init__(
        self,
        base_url: str = settings.kobo_base_url,
        api_token: str = settings.kobo_api_token,
        timeout_seconds: int = settings.kobo_request_timeout_seconds,
    ) -> None:
        self.base_url = base_url.rstrip("/")

        self.timeout_seconds = timeout_seconds

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Authorization": f"Token {api_token}",
                "Accept": "application/json",
            }
        )

        self._configure_retries()

    def _configure_retries(self) -> None:
        """
        Configure retries for transient failures.

        We retry requests that may fail temporarily, such as:
        - Connection errors
        - 429 Too Many Requests
        - 5xx server errors

        We do not blindly retry every HTTP status.
        """

        retry_strategy = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1,
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],
            allowed_methods=[
                "GET",
            ],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
        )

        self.session.mount(
            "https://",
            adapter,
        )

    def _build_url(self, path: str) -> str:
        """
        Build a complete API URL from a relative API path.
        """

        return f"{self.base_url}/{path.lstrip('/')}"

    def _handle_response(self, response: Response) -> None:
        """
        Convert unsuccessful HTTP responses into KoboAPIError.
        """

        if response.ok:
            return

        try:
            response_body = response.json()

        except ValueError:
            response_body = response.text

        raise KoboAPIError(
            "Kobo API request failed "
            f"with status {response.status_code}: "
            f"{response_body}"
        )

    def _get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a GET request and return the decoded JSON response.
        """

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout_seconds,
            )

        except requests.RequestException as error:
            raise KoboAPIError(
                f"Unable to connect to Kobo API: {error}"
            ) from error

        self._handle_response(response)

        try:
            return response.json()

        except ValueError as error:
            raise KoboAPIError(
                "Kobo API returned an invalid JSON response."
            ) from error

    def get_asset(
        self,
        asset_uid: str | None = None,
    ) -> KoboAsset:
        """
        Retrieve information about one Kobo project/asset.
        """

        uid = asset_uid or settings.kobo_asset_uid

        url = self._build_url(
            f"/api/v2/assets/{uid}/"
        )

        response_data = self._get(url)

        return KoboAsset.model_validate(
            response_data
        )

    def list_survey_assets(
        self,
    ) -> list[KoboAsset]:
        """
        Retrieve survey assets available to the authenticated user.

        This method handles pagination because the v2 API can return
        results across multiple pages.
        """

        url = self._build_url(
            "/api/v2/assets/"
        )

        params: dict[str, Any] | None = {
            "asset_type": "survey",
        }

        assets: list[KoboAsset] = []

        while url:
            response_data = self._get(
                url=url,
                params=params,
            )

            results = response_data.get(
                "results",
                [],
            )

            assets.extend(
                KoboAsset.model_validate(asset)
                for asset in results
            )

            url = response_data.get("next")

            # Kobo's `next` URL already contains its query parameters.
            params = None

        return assets

    def get_submission_page(
        self,
        asset_uid: str | None = None,
        url: str | None = None,
    ) -> KoboSubmissionPage:
        """
        Retrieve one page of Kobo submissions.

        If `url` is provided, it is assumed to be a pagination URL
        returned by Kobo's API.

        Otherwise, the default asset data endpoint is used.
        """

        if url is None:
            uid = asset_uid or settings.kobo_asset_uid

            url = self._build_url(
                f"/api/v2/assets/{uid}/data/"
            )

        response_data = self._get(
            url=url,
        )

        return KoboSubmissionPage.model_validate(
            response_data
        )

    def get_all_submissions(
        self,
        asset_uid: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve every submission for a Kobo asset.

        Kobo's v2 API paginates submission results.

        Example:

        First response:
            {
                "count": 1500,
                "next": "https://...page=2",
                "results": [...]
            }

        Second response:
            {
                "count": 1500,
                "next": null,
                "results": [...]
            }

        This method continues following `next` until all submissions
        have been retrieved.
        """

        submissions: list[dict[str, Any]] = []

        page = self.get_submission_page(
            asset_uid=asset_uid,
        )

        submissions.extend(
            page.results
        )

        next_url = page.next

        while next_url:
            page = self.get_submission_page(
                url=next_url,
            )

            submissions.extend(
                page.results
            )

            next_url = page.next

        return submissions

    def close(self) -> None:
        """
        Close the underlying HTTP session.
        """

        self.session.close()