# Claude.md - Project Context for AI Assistance

## Project Overview

**propresenter-slides** is a Python CLI tool that provides remote control interface for ProPresenter presentations via its REST APIs.

## Key Structure

- **src/propresenter_slides/main.py** - Main module containing:
  - `ProPresenterController` - API client class for ProPresenter communication
  - `interactive_prompt()` - CLI interactive loop for user commands
  - `main()` - CLI entry point with argument parsing

- **pyproject.toml** - Poetry configuration with console script entry point
- **README.md** - Project documentation with installation and usage instructions

## Core Functionality

### ProPresenterController Methods
- `next_slide()` - Advance to next slide (GET v1/presentation/active/next/trigger)
- `previous_slide()` - Go to previous slide (GET v1/presentation/active/previous/trigger)
- `go_to_slide(slide_index)` - Jump to specific slide by index (0-indexed)
- `get_status()` - Fetch current slide status (GET v1/status/slide)
- `get_active_presentation()` - Get currently active presentation details
- `get_active_playlist()` - Get currently active playlist details
- `ensure_presentation_active()` - Ensure a presentation is active (activates first in playlist if needed)
- `_request()` - Generic HTTP request handler

### CLI Commands
- `n` - Next slide
- `b` - Previous slide (back)
- `<number>` - Go to specific slide index (0-indexed, so 0 = first slide)
- `q` - Quit

## Common Tasks

### Adding New API Endpoints
1. Add method to `ProPresenterController` class
2. Use `self._request()` for HTTP calls
3. Return boolean for success or dict for data
4. Add corresponding command to `interactive_prompt()` if user-facing

### Modifying CLI Arguments
Edit the argparse section in `main()` to add/modify command-line flags.

### Installation & Development
```bash
poetry install
poetry run propresenter-slides --host=<host>
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
poetry run pytest --cov=propresenter_slides
```

## Development Notes

- Uses requests library for HTTP communication
- Base API URL: `http://{host}:{port}` (endpoints start with v1/)
- Defaults: localhost:1025 with 5-second timeout
- Connection verified on startup before entering interactive mode
- API endpoints use 0-indexed slide indices
- All slide control requests use GET method with /trigger endpoints
