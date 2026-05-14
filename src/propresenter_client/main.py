"""
Main module for ProPresenter API interface
"""

import argparse
import logging
import requests
import sys
from typing import Optional

logger = logging.getLogger(__name__)


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
            logger.debug(f"Request failed: {e}")
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

    def get_slide_position(self) -> Optional[tuple[int, int]]:
        """
        Get the current slide position and total slide count.

        Returns:
            A tuple of (current_slide_number, total_slides) in 1-indexed form,
            or None if the slide position cannot be determined from status.
        """
        status = self.get_status()
        if not status or not isinstance(status, dict):
            return None

        current = None
        total = None

        if "currentSlide" in status and isinstance(status["currentSlide"], dict):
            current = status["currentSlide"].get("index")
            if current is None:
                current = status["currentSlide"].get("number")
            total = status["currentSlide"].get("total")
            if total is None:
                total = status["currentSlide"].get("count")

        if current is None and "slide" in status and isinstance(status["slide"], dict):
            current = status["slide"].get("index")
            if current is None:
                current = status["slide"].get("number")
            total = status["slide"].get("total")
            if total is None:
                total = status["slide"].get("count")

        if current is None:
            for key in ("currentSlide", "slideIndex", "currentSlideIndex"):
                if key in status:
                    current = status[key]
                    break

        if total is None:
            for key in ("slideCount", "totalSlides", "slideTotal", "totalSlideCount"):
                if key in status:
                    total = status[key]
                    break

        if isinstance(current, int) and isinstance(total, int):
            return current + 1, total

        return None

    def go_to_slide(self, slide_number: int) -> bool:
        """
        Go to a specific slide number.

        Args:
            slide_number: The slide number to navigate to (1-indexed)

        Returns:
            True if successful, False otherwise
        """
        if slide_number <= 0:
            slide_number = 1  # Ensure slide number is at least 1

        api_slide_number = max(slide_number - 1, 0)

        result = self._request(
            "GET",
            f"v1/presentation/active/{api_slide_number}/trigger"
        )
        return result is not None

    def get_slide_index(self, chunked: bool = False) -> Optional[int]:
        """
        Get the zero-based index of the currently active slide.

        Args:
            chunked: If True, uses chunked slide indexing. Default False
                     returns a flat index across the whole presentation.

        Returns:
            Zero-based slide index, or None if it cannot be determined.
        """
        result = self._request(
            "GET", "v1/presentation/slide_index",
            params={"chunked": str(chunked).lower()}
        )
        logger.debug("get_slide_index response: %s", result)
        if result is None:
            return None
        if isinstance(result, int):
            return result
        if isinstance(result, dict):
            # Bare index at top level
            for key in ("slideIndex", "slide_index", "index"):
                val = result.get(key)
                if isinstance(val, int):
                    return val
            # Nested one level under a container key — check container first so we
            # don't accidentally pick up a sibling id.index from presentation metadata.
            for container in ("presentation_index", "presentationSlideIndex"):
                nested = result.get(container)
                if isinstance(nested, dict):
                    for key in ("slideIndex", "slide_index", "index"):
                        val = nested.get(key)
                        if isinstance(val, int):
                            return val
        return None

    def get_active_presentation(self) -> Optional[dict]:
        """
        Get the currently active presentation.

        Returns:
            Presentation details if available, None if request fails
        """
        return self._request("GET", "v1/presentation/active")

    def get_active_presentation_uuid(self) -> Optional[str]:
        """
        Get the UUID of the currently active presentation.

        Returns:
            UUID string if found, None if the active presentation cannot be
            reached or its UUID cannot be parsed from the response.
        """
        data = self.get_active_presentation()
        if not data:
            return None
        return ProPresenterController._extract_uuid(data)

    @staticmethod
    def _extract_uuid(data: object) -> Optional[str]:
        """Recursively locate a presentation UUID in a ProPresenter API response."""
        if not isinstance(data, dict):
            return None
        for key in ("uuid", "presentationId", "presentationUUID"):
            val = data.get(key)
            if isinstance(val, str) and val:
                return val
        for key in ("presentation", "id"):
            result = ProPresenterController._extract_uuid(data.get(key))
            if result:
                return result
        return None

    @staticmethod
    def find_slides(details: object) -> list:
        """
        Recursively collect ALL slides from a presentation details response,
        flattening across every group so the returned list is in presentation order.

        Args:
            details: The response payload from get_presentation_details()

        Returns:
            Flat list of all slide objects across all groups, or [] if none found.
        """
        if isinstance(details, dict):
            slides = details.get("slides")
            if isinstance(slides, list):
                return slides  # this dict is a group — return its slides directly
            all_slides: list = []
            for value in details.values():
                all_slides.extend(ProPresenterController.find_slides(value))
            return all_slides
        elif isinstance(details, list):
            all_slides = []
            for item in details:
                all_slides.extend(ProPresenterController.find_slides(item))
            return all_slides
        return []

    def get_library(self, library_name: str) -> Optional[dict]:
        """
        Get a named library's contents.

        Args:
            library_name: The library name to query

        Returns:
            Library data if available, None if request fails
        """
        return self._request("GET", f"v1/library/{library_name}")

    def get_library_default(self) -> Optional[dict]:
        """
        Get the Default library contents.

        Returns:
            Library data if available, None if request fails
        """
        return self.get_library("Default")

    def find_presentation_uuid_by_name(
        self, presentation_name: str, library_data: Optional[dict]
    ) -> Optional[str]:
        """
        Find a presentation UUID in the Default library by presentation name.

        Uses case-insensitive substring matching on common title fields.

        Args:
            presentation_name: The presentation name to search for
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

        search = presentation_name.strip().lower()

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

    def get_presentation_details(self, uuid: str) -> Optional[dict]:
        """
        Get details for a presentation by UUID.

        Args:
            uuid: The presentation UUID to fetch details for

        Returns:
            Presentation details if available, None if request fails
        """
        return self._request("GET", f"v1/presentation/{uuid}")

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

    def activate_first_library_presentation(self, library_name: str) -> bool:
        """
        Activate the first presentation in the specified library.

        Args:
            library_name: The library name to activate the first presentation from

        Returns:
            True if activation request succeeded, False otherwise
        """
        result = self._request("GET", f"v1/library/{library_name}/0/trigger")
        return result is not None


def _get_command() -> str:
    """Read a command without requiring Enter for single-char keys (n, b, q).
    Digits are buffered until Enter is pressed. Falls back to input() on
    platforms that don't support raw terminal mode."""
    try:
        import tty
        import termios
    except ImportError:
        return input().strip().lower()

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    buf = ""
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == "\x03":  # Ctrl+C
                raise KeyboardInterrupt
            if ch == "\x1b":  # Escape — clear digit buffer
                if buf:
                    sys.stdout.write("\r" + " " * (len("Enter command: ") + len(buf)))
                    sys.stdout.write("\rEnter command: ")
                    sys.stdout.flush()
                    buf = ""
                continue
            if not buf and ch.lower() in ("n", "b", "q"):
                sys.stdout.write(ch.lower() + "\n")
                sys.stdout.flush()
                return ch.lower()
            if ch.isdigit():
                buf += ch
                sys.stdout.write(ch)
                sys.stdout.flush()
            elif ch in ("\r", "\n") and buf:
                sys.stdout.write("\n")
                sys.stdout.flush()
                return buf
            elif ch in ("\x7f", "\x08") and buf:  # Backspace
                buf = buf[:-1]
                sys.stdout.write("\b \b")
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def interactive_prompt(controller: ProPresenterController) -> None:
    """
    Start an interactive prompt for controlling the presentation.

    Supported commands:
    - 'n': next slide
    - 'b': previous slide
    - <number>: go to specific slide number (1-indexed)
    - 'q': quit
    """
    print("\n=== ProPresenter Slide Controller ===")
    print("Commands: 'n' (next), 'b' (back), <number> (go to slide number), 'q' (quit)")
    print("Note: Slide numbers are 1-indexed (first slide = 1)")
    print("====================================\n")

    while True:
        try:
            sys.stdout.write("Enter command: ")
            sys.stdout.flush()
            user_input = _get_command()

            if not user_input:
                continue

            if user_input == 'q':
                print("Exiting...")
                break
            elif user_input == 'n':
                slide_position = controller.get_slide_position()
                if slide_position:
                    current_slide, total_slides = slide_position
                    if current_slide >= total_slides:
                        print("Cannot go beyond the last slide. Prompt attempted to go beyond the last slide.")
                        continue
                if controller.next_slide():
                    print("✓ Moved to next slide")
                else:
                    print("✗ Failed to move to next slide")
            elif user_input == 'b':
                slide_position = controller.get_slide_position()
                if slide_position:
                    current_slide, _ = slide_position
                    if current_slide <= 1:
                        print("Cannot go before the first slide. Prompt attempted to go beyond the first slide.")
                        continue
                if controller.previous_slide():
                    print("✓ Moved to previous slide")
                else:
                    print("✗ Failed to move to previous slide")
            else:
                # Try to parse as slide number
                try:
                    slide_num = int(user_input)
                    if slide_num <= 0:
                        print("Invalid slide number. Use 1 or greater.")
                        continue
                    slide_position = controller.get_slide_position()
                    if slide_position:
                        _, total_slides = slide_position
                        if slide_num > total_slides:
                            print("Cannot go beyond the last slide. Prompt attempted to go beyond the last slide.")
                            continue
                    if controller.go_to_slide(slide_num):
                        print(f"✓ Moved to slide {slide_num}")
                    else:
                        print(f"✗ Failed to move to slide {slide_num}")
                except ValueError:
                    print("Invalid command. Use 'n', 'b', a slide number (1-based), or 'q' to quit.")
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
        "--library",
        type=str,
        default="Default",
        help="Library name to use for presentation lookup and default activation (default: Default)"
    )
    parser.add_argument(
        "--presentation",
        type=str,
        help="Presentation title to activate from the configured library before entering interactive mode"
    )
    parser.add_argument(
        "--list-details",
        action="store_true",
        help="Print details for the specified presentation and exit (requires --presentation)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        help="Set logging verbosity for request diagnostics (default: WARNING)"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

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

    if args.list_details and not args.presentation:
        print("Error: --list-details requires --presentation")
        sys.exit(1)

    if args.presentation:
        library = controller.get_library(args.library)
        if library is None:
            print(f"Error: Could not query {args.library} library at {args.host}:{args.port}")
            sys.exit(1)

        presentation_uuid = controller.find_presentation_uuid_by_name(args.presentation, library)
        if presentation_uuid is None:
            print(f"Error: Presentation '{args.presentation}' not found in {args.library} library")
            sys.exit(1)

        if args.list_details:
            details = controller.get_presentation_details(presentation_uuid)
            if details is None:
                print(f"Error: Could not fetch details for '{args.presentation}' (UUID: {presentation_uuid})")
                sys.exit(1)
            import json
            print(json.dumps(details, indent=2))
            return

        if controller.activate_presentation(presentation_uuid):
            print(f"Activated '{args.presentation}' (UUID: {presentation_uuid})")
        else:
            print(f"Error: Failed to activate presentation UUID {presentation_uuid}")
            sys.exit(1)
    else:
        # Default behavior: activate first presentation in configured library
        if controller.activate_first_library_presentation(args.library):
            print(f"Activated first presentation in {args.library} library")
        else:
            print(f"Warning: Could not activate first presentation in {args.library} library")

    interactive_prompt(controller)


if __name__ == "__main__":
    main()
