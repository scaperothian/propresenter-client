# propresenter-client

Python client for the ProPresenter REST API.

## Description

A general-purpose Python library and CLI for interacting with ProPresenter's REST API. Provides a `ProPresenterController` class for programmatic access to any ProPresenter API endpoint, plus an interactive **presentation mode** CLI for live slide control.

## Features

- `ProPresenterController` class covering common ProPresenter API endpoints
- Interactive presentation mode for live slide navigation
- Extensible design — add new API endpoints as methods over time

## Installation

```bash
pip install propresenter-client
```

## Development Setup

```bash
# Install dependencies
poetry install

# Run commands within the Poetry environment
poetry run propresenter-client --host=<your-host>
```

## Quick Start

```python
from propresenter_client import ProPresenterController

controller = ProPresenterController(host="localhost", port=1025)

# Slide control
controller.next_slide()
controller.previous_slide()
controller.go_to_slide(1)  # 1-indexed

# Presentations
controller.activate_presentation("92B5E6E2-5E99-4F54-BAD3-6FBD7D2EE675")
controller.get_presentation_details("92B5E6E2-5E99-4F54-BAD3-6FBD7D2EE675")
controller.activate_first_library_presentation("Default")
```

## Interactive Presentation Mode

```bash
# Default: activates first presentation in Default library
propresenter-client --host=192.168.1.100

# Activate a specific presentation by name before entering interactive mode
propresenter-client --host=192.168.1.100 --presentation="Amazing Grace"

# Print presentation details and exit (no interactive mode)
propresenter-client --host=192.168.1.100 --presentation="Amazing Grace" --list-details

# Use a different library
propresenter-client --host=192.168.1.100 --library="Worship"

# Enable request diagnostics
propresenter-client --host=192.168.1.100 --log-level=DEBUG
```

Interactive commands (no Enter required for single-key commands):
- `n` — Next slide
- `b` — Back to previous slide
- `q` — Quit
- `1`, `2`, `3`, … — Go to specific slide (1-indexed, press Enter to confirm)
- `Escape` — Cancel a partially typed slide number

## Testing

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

# Generate coverage report
poetry run pytest --cov=propresenter_client
```

## Requirements

- Python 3.10+
- requests

## License

MIT
