# Gimer

A CLI tool to make Git merge operations easier.

## Installation

### From Binary

Download the latest binary from the [Releases](https://github.com/shouki-s/gimer/releases) page.

## Usage

```bash
gimer <repository_url> --source <source_branch> --target <target_branch> [OPTIONS]
```

### Options

- `--source`: Source branch to merge from
- `--target`: Target branch to merge into
- `--dry-run`: Show what would be done without actually doing it
- `--cleanup`: Remove local repository after completion
- `-y, --no-confirm`: Do not confirm
- `--confirm-all`: Confirm before executing all git commands

### Example

```bash
gimer https://github.com/username/repo.git --source feature-branch --target main
```

### Note: Manually merging

When merge conflicts occur, you may need to resolve them manually. To use a visual merge tool, configure your Git mergetool:

```bash
# Configure a merge tool (example with vscode)
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Or with vimdiff
git config --global merge.tool vimdiff

# Or with kdiff3
git config --global merge.tool kdiff3
```

After resolving conflicts, gimer will automatically complete the merge. If you need to manually complete the merge outside of gimer, use:

```bash
# If you resolved conflicts manually (not using mergetool)
git add .
git commit -m "Resolve merge conflicts"
```

## Development

```bash
# Clone the repository
git clone https://github.com/shouki-s/gimer.git
cd gimer

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Build package
uv build

# Build binary
uv run pyinstaller gimer.spec
```

The binary will be created in the `dist` directory.
