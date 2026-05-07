"""
Main module for ProPresenter API interface
"""

import requests
from typing import Optional


class ProPresenterController:
    """Interface for controlling ProPresenter via its APIs"""

    def __init__(self, host: str = "localhost", port: int = 5000, timeout: int = 5):
        """
        Initialize the ProPresenter controller.

        Args:
            host: The hostname or IP address of the ProPresenter instance
            port: The port number for the ProPresenter API
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[dict]:
        """
        Make a request to the ProPresenter API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response JSON or None if request fails
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.request(
                method, url, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def next_slide(self) -> bool:
        """Advance to the next slide."""
        result = self._request("POST", "api/v1/presentation/slides/next")
        return result is not None

    def previous_slide(self) -> bool:
        """Go to the previous slide."""
        result = self._request("POST", "api/v1/presentation/slides/previous")
        return result is not None

    def get_status(self) -> Optional[dict]:
        """Get the current presentation status."""
        return self._request("GET", "api/v1/presentation/status")
