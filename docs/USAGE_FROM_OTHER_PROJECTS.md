# Using cognitive-memory-core from Other Projects

If you want to use the `cmemory` CLI from a different project directory, you need to install it first.

## Option 1: Install as Editable Package (Recommended)

From your other project directory:

```bash
# Navigate to your project
cd E:\Repos\ai_human_collab

# Install cognitive-memory-core from local path
uv pip install -e E:\Repos\cognitive-memory-core

# Now you can use cmemory
uv run cmemory --help
uv run cmemory list-blocks
```

## Option 2: Use from Source Directory

Always run commands from the `cognitive-memory-core` directory:

```bash
# Navigate to cognitive-memory-core
cd E:\Repos\cognitive-memory-core

# Run commands
uv run cmemory --help
uv run cmemory list-blocks
```

## Option 3: Add as Dependency

If `ai_human_collab` has a `pyproject.toml` or `requirements.txt`, add:

```toml
# In pyproject.toml
dependencies = [
    "cognitive-memory-core @ file:///E:/Repos/cognitive-memory-core",
]
```

Or:

```txt
# In requirements.txt
-e E:\Repos\cognitive-memory-core
```

Then install:

```bash
uv pip install -e .
```

## Why This Happens

The `cmemory` command is only available in virtual environments where `cognitive-memory-core` is installed. When you're in a different project (`ai_human_collab`), that project's virtual environment doesn't have `cognitive-memory-core` installed, so the command isn't available.

## Quick Check

To see if `cmemory` is available:

```bash
# Check if installed
uv run which cmemory  # Linux/Mac
uv run where cmemory  # Windows

# Or try to run it
uv run cmemory --help
```

If it fails with "program not found", you need to install it in that project's environment.

