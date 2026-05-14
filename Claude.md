# Claude.md - Project Context for AI Assistance

## Project Overview

**propresenter-client** is a general-purpose Python client and CLI for the ProPresenter REST API. It exposes a `ProPresenterController` class for programmatic access to any ProPresenter endpoint, and ships an interactive **presentation mode** CLI as a built-in usage example. New modes can be added over time alongside presentation mode.

## Key Structure

- **src/propresenter_client/main.py** - Main module containing:
  - `ProPresenterController` - API client class for ProPresenter communication
  - `_get_command()` - Raw terminal input helper for single-keypress commands
  - `interactive_prompt()` - CLI interactive loop for user commands
  - `main()` - CLI entry point with argument parsing

- **pyproject.toml** - Poetry configuration with console script entry point
- **README.md** - Project documentation with installation and usage instructions

## Core Functionality

### ProPresenterController Methods
- `next_slide()` - Advance to next slide (GET v1/presentation/active/next/trigger)
- `previous_slide()` - Go to previous slide (GET v1/presentation/active/previous/trigger)
- `go_to_slide(slide_index)` - Jump to specific slide by number (1-indexed)
- `get_status()` - Fetch current slide status (GET v1/status/slide)
- `get_slide_position()` - Get current slide position and total slide count
- `get_active_presentation()` - Get currently active presentation details
- `get_library(library_name)` - Get a named library's contents
- `get_library_default()` - Get Default library contents (GET v1/library/Default)
- `find_presentation_uuid_by_name(presentation_name, library_data)` - Find presentation UUID by name in library
- `get_presentation_details(uuid)` - Fetch full details for a presentation by UUID (GET v1/presentation/{uuid})
- `activate_presentation(uuid)` - Activate presentation by UUID (GET v1/presentation/{uuid}/trigger)
- `activate_first_library_presentation(library_name)` - Activate first presentation in library (GET v1/library/{library}/0/trigger)
- `_request()` - Generic HTTP request handler

### CLI Arguments
- `--host` - ProPresenter host/IP address (default: localhost)
- `--port` - ProPresenter port (default: 1025)
- `--timeout` - Request timeout in seconds (default: 5)
- `--library` - Library name to use for presentation lookup and default activation (default: Default)
- `--presentation` - Presentation title to activate from configured library before interactive mode
- `--list-details` - Print full JSON details for the specified presentation and exit (requires `--presentation`)
- `--log-level` - Set logging verbosity for request diagnostics (default: WARNING)

### CLI Commands
- `n` - Next slide (fires immediately, no Enter needed)
- `b` - Previous slide / back (fires immediately, no Enter needed)
- `q` - Quit (fires immediately, no Enter needed)
- `<number>` + Enter - Go to specific slide number (1-indexed, so 1 = first slide)
- `Escape` - Cancel a partially typed slide number

Input uses raw terminal mode (`tty`/`termios`) on Unix/macOS so single-char commands register on keypress. Falls back to `input()` on unsupported platforms. The `_get_command()` helper in `main.py` handles this logic.

## Common Tasks

### Adding New API Endpoints
1. Add method to `ProPresenterController` class
2. Use `self._request()` for HTTP calls
3. Return boolean for success or dict for data
4. Add corresponding command to `interactive_prompt()` if user-facing

### Adding Presentation Activation
1. Add method to query library: `GET v1/library/{library_name}`
2. Add method to find presentation by name in library response
3. Add method to activate presentation: `GET v1/presentation/{uuid}/trigger`
4. Add CLI argument and logic in `main()` to handle activation before interactive mode

### Modifying CLI Arguments
Edit the argparse section in `main()` to add/modify command-line flags.

### Installation & Development
```bash
poetry install
poetry run propresenter-client --host=<host>
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_propresenter_controller.py -v

# Run specific test class
poetry run pytest tests/test_propresenter_controller.py::TestProPresenterController -v

# Run individual test
poetry run pytest tests/test_propresenter_controller.py::TestProPresenterController::test_get_status_success -v

# Run tests matching a pattern
poetry run pytest -k "test_get" -v

# Run with coverage report
poetry run pytest --cov=propresenter_client
```

## Development Notes

- Uses requests library for HTTP communication
- Base API URL: `http://{host}:{port}` (endpoints start with v1/)
- Defaults: localhost:1025 with 5-second timeout
- Connection verified on startup before entering interactive mode
- Default behavior: activates first presentation in configured library
- `--library` option: searches specified library for matching presentation name, then activates it (default: Default); also used for first-presentation activation if no presentation specified
- `go_to_slide` uses 1-indexed slide numbers for presentation navigation
- All slide control requests use GET method with /trigger endpoints
