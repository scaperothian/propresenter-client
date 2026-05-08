# propresenter-slides

Interface with ProPresenter's APIs to cue slides remotely using Python.

## Description

This Python library provides a convenient interface for interacting with ProPresenter's APIs, allowing you to programmatically control and cue slides in presentations remotely.

## Features

- Remote slide control via ProPresenter APIs
- Easy-to-use Python interface
- Support for common slide operations

## Installation

```bash
pip install propresenter-slides
```

## Development Setup

To set up the development environment with Poetry:

```bash
# Install dependencies
poetry install

# Activate the virtual environment
poetry shell

# Or run commands directly within the Poetry environment
poetry run propresenter-slides --host=<your-host>
```

## Quick Start

```python
from propresenter_slides import ProPresenterController

# Initialize controller
controller = ProPresenterController(host="localhost", port=1025)

# Control slides
controller.next_slide()
controller.previous_slide()
controller.go_to_slide(1)  # Go to first slide (1-indexed)

# Activate specific presentation by UUID
controller.activate_presentation("92B5E6E2-5E99-4F54-BAD3-6FBD7D2EE675")

# Activate first presentation in a library
controller.activate_first_library_presentation("Default")
```

## Interactive Mode

```bash
# Default behavior: activates first presentation in Default library
propresenter-slides --host=192.168.1.100

# Activate specific presentation by name before entering interactive mode
propresenter-slides --host=192.168.1.100 --presentation="Amazing Grace"

# Use a different library
propresenter-slides --host=192.168.1.100 --library="Worship"
```

You can also enable request diagnostics with logging:

```bash
propresenter-slides --host=192.168.1.100 --log-level=DEBUG
```

Then use:
- `n` - Next slide
- `b` - Back to previous slide
- `1`, `2`, `3`, etc. - Go to specific slide (1-indexed)
- `q` - Quit

### Default Behavior

When no `--presentation` argument is provided, the tool automatically activates the first presentation in the configured library (`GET /v1/library/<library>/0/trigger`).

When `--presentation` is specified, it searches the configured library for a matching presentation name and activates it before entering interactive mode.

### CLI Override

CLI arguments allow you to customize behavior:

```bash
propresenter-slides --library="Worship" --log-level=DEBUG
```

## Testing

Run the test suite:

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
poetry run pytest -k "test_next" -v

# Generate coverage report
poetry run pytest --cov=propresenter_slides
```

## Requirements

- Python 3.10+
- requests

## License

MIT

## Contributing

Contributions are welcome! Please read our contributing guidelines for details on our code of conduct and the process for submitting pull requests.
