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
gimer <repository_url> <target_branch> <source_branch> [OPTIONS]
```

### Options

- `--dry-run`: Show what would be done without actually doing it
- `--cleanup`: Remove local repository after completion
- `--confirm`: Confirm before executing git commands
  - `origin`: Confirm only for commands affecting origin
  - `all`: Confirm for all git commands

### Example

```bash
gimer https://github.com/username/repo.git main feature-branch
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/gimer.git
cd gimer

# Install dependencies
uv sync --all-extras

# Run tests
pytest

# Build package
uv build

# Build binary
uv run pyinstaller gimer.spec
```

The binary will be created in the `dist` directory.
