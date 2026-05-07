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
controller.go_to_slide(0)  # Go to first slide (0-indexed)
```

## Interactive Mode

```bash
propresenter-slides --host=192.168.1.100
```

Then use:
- `n` - Next slide
- `b` - Back to previous slide
- `0`, `1`, `2`, etc. - Go to specific slide (0-indexed)
- `q` - Quit

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
