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
            slide_number: The slide index to navigate to (1-indexed)

        Returns:
            True if successful, False otherwise
        """
        if slide_number <= 0:
            slide_number = 1  # Ensure slide number is at least 1

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

    def get_library_default(self) -> Optional[dict]:
        """
        Get the Default library contents.

        Returns:
            Library data if available, None if request fails
        """
        return self._request("GET", "v1/library/Default")

    def find_presentation_uuid_by_name(
        self, song_name: str, library_data: Optional[dict]
    ) -> Optional[str]:
        """
        Find a presentation UUID in the Default library by song name.

        Uses case-insensitive substring matching on common title fields.

        Args:
            song_name: The song/presentation name to search for
            library_data: The library response payload

        Returns:
            The matching presentation UUID, or None if not found
        """
        if not library_data:
            return None

        items = []
        if isinstance(library_data, dict):
            if "items" in library_data and isinstance(library_data["items"], list):
                items = library_data["items"]
            elif "presentations" in library_data and isinstance(library_data["presentations"], list):
                items = library_data["presentations"]
            else:
                items = [library_data]
        elif isinstance(library_data, list):
            items = library_data

        search = song_name.strip().lower()

        for entry in items:
            if not isinstance(entry, dict):
                continue

            title = (
                entry.get("name")
                or entry.get("title")
                or entry.get("presentationName")
                or entry.get("presentationTitle")
                or entry.get("songName")
            )
            uuid = (
                entry.get("uuid")
                or entry.get("id")
                or entry.get("presentationId")
                or entry.get("presentationUUID")
            )

            if title and uuid and search in title.lower():
                return uuid

        return None

    def activate_presentation(self, uuid: str) -> bool:
        """
        Activate a presentation by UUID.

        Args:
            uuid: The presentation UUID to activate

        Returns:
            True if activation request succeeded, False otherwise
        """
        result = self._request("GET", f"v1/presentation/{uuid}/trigger")
        return result is not None

    def ensure_presentation_active(self) -> bool:
        """
        Ensure a presentation is active. If none is active, activate the first presentation
        in the active playlist.

        Returns:
            True if a presentation is active, False otherwise
        """
        active = self.get_active_presentation()
        if active and isinstance(active, dict):
            return True

        playlist = self.get_active_playlist()
        if playlist and isinstance(playlist, dict) and "presentation" in playlist:
            result = self._request("GET", "v1/playlist/active/presentation/trigger")
            if result is not None:
                return True

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
    parser.add_argument(
        "--song",
        type=str,
        help="Song title to activate from the Default library before entering interactive mode"
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

    if args.song:
        library = controller.get_library_default()
        if library is None:
            print(f"Error: Could not query Default library at {args.host}:{args.port}")
            sys.exit(1)

        song_uuid = controller.find_presentation_uuid_by_name(args.song, library)
        if song_uuid is None:
            print(f"Error: Song '{args.song}' not found in Default library")
            sys.exit(1)

        if controller.activate_presentation(song_uuid):
            print(f"Activated '{args.song}' (UUID: {song_uuid})")
        else:
            print(f"Error: Failed to activate presentation UUID {song_uuid}")
            sys.exit(1)

    # Ensure a presentation is active
    if not controller.ensure_presentation_active():
        print("Warning: Could not activate a presentation")
    else:
        print("Presentation is active")

    interactive_prompt(controller)


if __name__ == "__main__":
    main()
