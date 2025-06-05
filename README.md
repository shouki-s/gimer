# Gimer

A CLI tool to make Git merge operations easier.

## Installation

### From Binary (Recommended)

Download the latest binary from the [Releases](https://github.com/yourusername/gimer/releases) page.

### From Source

```bash
pip install gimer
```

## Usage

```bash
gimer merge <branch_name>
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/gimer.git
cd gimer

# Install dependencies
uv sync

# Run tests
pytest

# Build binary
uv run pyinstaller gimer.spec
```

The binary will be created in the `dist` directory.
