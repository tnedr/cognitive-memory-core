# UV Cache Workflow Guidelines

## 🎯 Core Principle: Minimal .venv, Maximum Cache

### The UV Cache Philosophy

- **`.venv`**: Minimal, lightweight, mostly symlinks
- **`E:\uv-cache`**: Heavy lifting, all packages stored here
- **Result**: Fast installs, minimal disk usage per project

> 🧭 **Monorepo and Multi-Language Compatibility**
>
> - In **single-package** Python projects, use `.venv` and `packages/` as usual.
> - In **multi-package monorepos**, keep a **single `.venv` in the repository root** and store code under `python-packages/` (or `packages/` if Python-only).
> - Define `[tool.uv] workspace = true` in the root `pyproject.toml` so `uv` automatically detects all sub-packages.
>
> This allows consistent caching and minimal `.venv` usage across the entire repo.

## 📁 Cache Configuration

### Global Cache Location

```bash
# Set once, use everywhere
setx UV_CACHE_DIR "E:\uv-cache"
```

### Project Structure

```
E:\Repos\marketing-pipeline\
├── .venv/                    # Shared, minimal virtual environment
├── packages/ or python-packages/  # All Python source packages
└── pyproject.toml             # Root workspace definition

E:\uv-cache\                 # Global cache (can be 10GB+)
├── wheels/                 # All wheel files
├── builds-v0/              # Build artifacts
└── installs/               # Installation metadata
```

## 🔧 UV Workflow Commands

### Project Setup

```bash
# Create minimal venv (uv handles the rest)
python -m venv .venv --symlinks

# Install with uv (uses cache automatically)
uv pip install -e .
```

### Development Workflow

```bash
# Install dependencies (from cache)
uv pip install -e .

# Run scripts (uses cached packages)
uv run python demo_simple.py

# Sync project (if uv.lock exists)
uv sync
```

### Cache Management

```bash
# Check cache location
uv cache dir

# Clean old cache entries
uv cache prune

# Show cache info
uv cache clean --help
```

## ✅ Expected Behavior

### .venv Should Be Minimal

```bash
# Check venv size (should be < 50MB for most projects)
Get-ChildItem .venv -Recurse | Measure-Object -Property Length -Sum
```

### Cache Should Be Large

```bash
# Check cache size (can be 10GB+)
Get-ChildItem E:\uv-cache -Recurse | Measure-Object -Property Length -Sum
```

### Package Installation

```bash
# When installing packages, you should see:
# "Using cached wheel from E:\uv-cache\..."
uv pip install numpy -v
```

## 🚫 Anti-Patterns (DO NOT USE)

### ❌ Don't Install Globally

```bash
# WRONG - Don't install packages globally
pip install numpy
```

### ❌ Don't Use pip Directly

```bash
# WRONG - Don't use pip in venv
.venv\Scripts\activate
pip install numpy
```

### ❌ Don't Copy Packages

```bash
# WRONG - Don't copy packages manually
copy E:\uv-cache\wheels\numpy-*.whl .venv\Lib\site-packages\
```

## ✅ Correct Patterns

### ✅ Use UV for Everything

```bash
# CORRECT - Use uv for all package management
uv pip install numpy
uv pip install -e .
uv run python script.py
```

### ✅ Let UV Handle Cache

```bash
# CORRECT - Let uv manage the cache automatically
uv pip install package-name
# UV automatically uses E:\uv-cache
```

### ✅ Use Project Configuration

```bash
# CORRECT - Use project-level configuration
uv pip install -e .
# Installs from pyproject.toml
```

## 🔍 Troubleshooting

### Large .venv Directory

```bash
# If .venv is too large, recreate it
Remove-Item .venv -Recurse -Force
python -m venv .venv --symlinks
uv pip install -e .
```

### Cache Not Working

```bash
# Check cache configuration
uv cache dir
echo $env:UV_CACHE_DIR

# Verify cache is being used
uv pip install numpy -v
# Should show "Using cached wheel from E:\uv-cache\..."
```

### Package Not Found

```bash
# Clear cache and reinstall
uv cache prune
uv pip install -e .
```

## 📊 Performance Expectations

### Installation Speed

- **First install**: Normal speed (downloading to cache)
- **Subsequent installs**: Very fast (from cache)
- **Cache hits**: Should see "Using cached wheel" messages

### Disk Usage

- **Per project .venv**: < 50MB typically
- **Global cache**: 5-15GB (shared across all projects)
- **Total savings**: 80-90% disk usage reduction

## 🔧 Development Workflow

### Daily Development

```bash
# Start development session
cd E:\Repos\marketing-pipeline

# Activate venv (minimal)
.\.venv\Scripts\activate

# Install/update dependencies
uv pip install -e .

# Run your code
python demo_simple.py
```

### New Project Setup

```bash
# Create new project
mkdir new-project
cd new-project

# Create minimal venv
python -m venv .venv --symlinks

# Install dependencies (uses global cache)
uv pip install -e .
```

### CI/CD Pipeline

```bash
# In CI/CD, use uv for consistency
uv pip install -e .
uv run python tests.py
```

## 🎯 Quality Gates

### Pre-commit Checks

```bash
# Check venv size
$venvSize = (Get-ChildItem .venv -Recurse | Measure-Object -Property Length -Sum).Sum
if ($venvSize -gt 100MB) {
    Write-Error "Venv too large: $venvSize bytes"
    exit 1
}

# Check cache usage
uv pip install numpy -v | Select-String "Using cached wheel"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Cache not being used"
    exit 1
}
```

### Health Checks

```bash
# Verify cache configuration
uv cache dir
# Should show: E:\uv-cache

# Check cache size
Get-ChildItem E:\uv-cache -Recurse | Measure-Object -Property Length -Sum
# Should be > 1GB for active development

# Verify venv is minimal
Get-ChildItem .venv -Recurse | Measure-Object -Property Length -Sum
# Should be < 100MB
```

## 📝 Documentation Requirements

### Project README

````markdown
## Development Setup

This project uses UV cache for efficient package management.

### Prerequisites

- Python 3.11+
- UV package manager
- UV_CACHE_DIR environment variable set

### Setup

```bash
# Install dependencies (uses global cache)
uv pip install -e .

# Run demo
uv run python demo_simple.py
```
````

### Cache Configuration

- Global cache: `E:\uv-cache`
- Project venv: Minimal, mostly symlinks
- Dependencies: Stored in global cache

````

## 🚀 Benefits

### Why UV Cache Matters
1. **Speed**: Fast installs from cache
2. **Space**: Minimal disk usage per project
3. **Consistency**: Same packages across projects
4. **Reliability**: No network issues for cached packages
5. **Development**: Quick project setup

### Performance Gains
- **Install time**: 10x faster for cached packages
- **Disk usage**: 80-90% reduction per project
- **Network usage**: Minimal after initial install
- **Development speed**: Instant project setup

## 🎯 Summary

**ALWAYS**:
- Use `uv pip install` for package management
- Let uv handle cache automatically
- Keep .venv minimal
- Use global cache for heavy packages

**NEVER**:
- Use pip directly in venv
- Install packages globally
- Copy packages manually
- Ignore cache configuration

**RESULT**: Fast, efficient, minimal disk usage development environment.

## 🧩 Workspace Integration Example

When using a shared `.venv` across multiple packages, define a workspace in the root `pyproject.toml`:

```toml
[project]
name = "marketing-pipeline-monorepo"
version = "0.1.0"

[tool.uv.workspace]
````

All sub-packages under `python-packages/` (or `packages/`) will be linked automatically.
All installs (`uv pip install -e .`) will use the global cache at `E:\uv-cache`.
