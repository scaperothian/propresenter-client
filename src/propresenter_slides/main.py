"""
Main module for ProPresenter API interface
"""

import argparse
import requests
import sys
from typing import Optional


class ProPresenterController:
    """Interface for controlling ProPresenter via its APIs"""

    def __init__(self, host: str = "localhost", port: int = 1025, timeout: int = 5):
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
            Response JSON if available, or empty dict if successful with no content, None if request fails
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.request(
                method, url, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            # Try to parse JSON, but some endpoints return no content
            if response.text:
                return response.json()
            else:
                return {}
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def next_slide(self) -> bool:
        """Advance to the next slide."""
        result = self._request("GET", "v1/presentation/active/next/trigger")
        return result is not None

    def previous_slide(self) -> bool:
        """Go to the previous slide."""
        result = self._request("GET", "v1/presentation/active/previous/trigger")
        return result is not None

    def get_status(self) -> Optional[dict]:
        """Get the current presentation status."""
        return self._request("GET", "v1/status/slide")

    def go_to_slide(self, slide_number: int) -> bool:
        """
        Go to a specific slide number.

        Args:
            slide_number: The slide index to navigate to (0-indexed)

        Returns:
            True if successful, False otherwise
        """
        result = self._request(
            "GET",
            f"v1/presentation/active/{slide_number}/trigger"
        )
        return result is not None

    def get_active_presentation(self) -> Optional[dict]:
        """
        Get the currently active presentation.

        Returns:
            Presentation details if available, None if request fails
        """
        return self._request("GET", "v1/presentation/active")

    def get_active_playlist(self) -> Optional[dict]:
        """
        Get the currently active playlist.

        Returns:
            Playlist details if available, None if request fails
        """
        return self._request("GET", "v1/playlist/active")

    def ensure_presentation_active(self) -> bool:
        """
        Ensure a presentation is active. If none is active, activate the first presentation
        in the active playlist.

        Returns:
            True if a presentation is active, False otherwise
        """
        active = self.get_active_presentation()
        if active['presentation'] is not None:
            return True
        else:
            #need to activate a presentation be default (i.e. the first one)

        # If no presentation is active, try to trigger the first presentation in active playlist
        playlist = self.get_active_playlist()
        if playlist and "presentation" in playlist:
            # Trigger the first presentation in the active playlist
            result = self._request("GET", "v1/playlist/active/presentation/trigger")
            return result is not None

        # Fallback: try to trigger the focused presentation
        result = self._request("GET", "v1/presentation/focused/trigger")
        return result is not None


def interactive_prompt(controller: ProPresenterController) -> None:
    """
    Start an interactive prompt for controlling the presentation.

    Supported commands:
    - 'n': next slide
    - 'b': previous slide
    - <number>: go to specific slide index (0-indexed)
    - 'q': quit
    """
    print("\n=== ProPresenter Slide Controller ===")
    print("Commands: 'n' (next), 'b' (back), <number> (go to slide index), 'q' (quit)")
    print("Note: Slide indices are 0-indexed (first slide = 0)")
    print("====================================\n")

    while True:
        try:
            user_input = input("Enter command: ").strip().lower()

            if not user_input:
                continue

            if user_input == 'q':
                print("Exiting...")
                break
            elif user_input == 'n':
                if controller.next_slide():
                    print("✓ Moved to next slide")
                else:
                    print("✗ Failed to move to next slide")
            elif user_input == 'b':
                if controller.previous_slide():
                    print("✓ Moved to previous slide")
                else:
                    print("✗ Failed to move to previous slide")
            else:
                # Try to parse as slide number
                try:
                    slide_num = int(user_input)
                    if controller.go_to_slide(slide_num):
                        print(f"✓ Moved to slide {slide_num}")
                    else:
                        print(f"✗ Failed to move to slide {slide_num}")
                except ValueError:
                    print("Invalid command. Use 'n', 'b', a slide index (0-based), or 'q' to quit.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Control ProPresenter presentations from the command line"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="ProPresenter host/IP address (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1025,
        help="ProPresenter port (default: 1025)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Request timeout in seconds (default: 5)"
    )

    args = parser.parse_args()

    controller = ProPresenterController(
        host=args.host,
        port=args.port,
        timeout=args.timeout
    )

    # Test connection
    status = controller.get_status()
    if status is None:
        print(f"Error: Could not connect to ProPresenter at {args.host}:{args.port}")
        sys.exit(1)

    print(f"Connected to ProPresenter at {args.host}:{args.port}")

    # Ensure a presentation is active
    if not controller.ensure_presentation_active():
        print("Warning: Could not activate a presentation")
    else:
        print("Presentation is active")

    interactive_prompt(controller)


if __name__ == "__main__":
    main()
