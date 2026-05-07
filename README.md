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

## Quick Start

```python
from propresenter_slides import ProPresenterController

# Initialize controller
controller = ProPresenterController(host="localhost", port=5000)

# Control slides
controller.next_slide()
controller.previous_slide()
```

## Requirements

- Python 3.8+
- requests

## License

MIT

## Contributing

Contributions are welcome! Please read our contributing guidelines for details on our code of conduct and the process for submitting pull requests.
