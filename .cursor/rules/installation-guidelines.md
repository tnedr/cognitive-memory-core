# Installation Guidelines for Marketing Pipeline

## 🎯 Core Principle: UV-First Installation Strategy

### The UV Installation Philosophy

- **ALWAYS use `uv pip install`** for package management
- **NEVER use `pip install`** directly in virtual environments
- **LET UV handle caching** automatically via `E:\uv-cache`
- **MINIMIZE .venv size** through efficient package linking

## 📦 Installation Workflow

### 1. Project Setup (First Time)

```bash
# Create minimal venv (uv handles the rest)
python -m venv .venv --symlinks

# Install project in development mode (uses cache)
uv pip install -e .

# Install additional dependencies (from cache)
uv pip install skia-python pyyaml requests
```

### 2. Daily Development

```bash
# Activate venv (minimal)
.\.venv\Scripts\activate

# Install new packages (uses cache)
uv pip install package-name

# Install from requirements (uses cache)
uv pip install -r requirements.txt

# Run scripts (uses cached packages)
uv run python script.py
```

### 3. Dependency Management

```bash
# Add to pyproject.toml dependencies
# Then install project
uv pip install -e .

# Or install specific packages
uv pip install numpy pandas matplotlib
```

## ✅ Correct Installation Patterns

### ✅ Project Dependencies

```bash
# CORRECT - Install project with all dependencies
uv pip install -e .

# CORRECT - Install specific packages
uv pip install skia-python pyyaml requests

# CORRECT - Install from requirements
uv pip install -r requirements.txt
```

### ✅ Development Dependencies

```bash
# CORRECT - Install dev dependencies
uv pip install pytest black mypy

# CORRECT - Install with extras
uv pip install -e .[dev,test]
```

### ✅ Package Management

```bash
# CORRECT - List installed packages
uv pip list

# CORRECT - Show package info
uv pip show package-name

# CORRECT - Check for updates
uv pip list --outdated
```

## 🚫 Anti-Patterns (DO NOT USE)

### ❌ Don't Use pip Directly

```bash
# WRONG - Don't use pip in venv
.\.venv\Scripts\activate
pip install numpy

# WRONG - Don't use pip globally
pip install --user package-name
```

### ❌ Don't Install Globally

```bash
# WRONG - Don't install system-wide
pip install --system package-name

# WRONG - Don't use --user flag
pip install --user package-name
```

### ❌ Don't Use conda/mamba

```bash
# WRONG - Don't mix package managers
conda install package-name
mamba install package-name
```

### ❌ Don't Copy Packages Manually

```bash
# WRONG - Don't copy packages
copy E:\uv-cache\wheels\*.whl .venv\Lib\site-packages\
```

## 🔧 UV Cache Integration

### Cache Configuration

```bash
# Verify cache location
uv cache dir
# Should show: E:\uv-cache

# Check cache usage
uv pip install numpy -v
# Should show: "Using cached wheel from E:\uv-cache\..."
```

### Cache Management

```bash
# Clean old cache entries
uv cache prune

# Show cache statistics
uv cache clean --help

# Force reinstall from cache
uv pip install --force-reinstall package-name
```

## 📊 Installation Performance

### Expected Behavior

```bash
# First install (downloads to cache)
uv pip install numpy
# Time: ~5-10 seconds

# Subsequent installs (from cache)
uv pip install numpy
# Time: ~1-2 seconds

# Cache hit messages
# "Using cached wheel from E:\uv-cache\..."
```

### Performance Metrics

- **Cache hits**: 90%+ for common packages
- **Install speed**: 10x faster from cache
- **Disk usage**: 80-90% reduction per project
- **Network usage**: Minimal after initial install

## 🎯 Installation Checklist

### Before Installing Any Package

- [ ] Is it using `uv pip install`?
- [ ] Is the cache configured correctly?
- [ ] Is the venv activated?
- [ ] Are we installing the right package?

### After Installation

- [ ] Did it use cached packages?
- [ ] Is the venv still minimal?
- [ ] Are there any errors?
- [ ] Can we import the package?

## 🔍 Troubleshooting

### Common Issues

#### Package Not Found

```bash
# Check if package exists
uv pip search package-name

# Try different package name
uv pip install package-name-alternative

# Check PyPI directly
# https://pypi.org/project/package-name/
```

#### Cache Not Working

```bash
# Check cache configuration
uv cache dir
echo $env:UV_CACHE_DIR

# Clear cache and reinstall
uv cache prune
uv pip install package-name
```

#### Import Errors

```bash
# Check if package is installed
uv pip list | findstr package-name

# Reinstall package
uv pip install --force-reinstall package-name

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Large .venv Directory

```bash
# Check venv size
Get-ChildItem .venv -Recurse | Measure-Object -Property Length -Sum

# If too large, recreate venv
Remove-Item .venv -Recurse -Force
python -m venv .venv --symlinks
uv pip install -e .
```

## 📋 Package Categories

### Core Dependencies (Always Install)

```bash
# Project dependencies
uv pip install -e .

# Essential packages
uv pip install numpy pandas matplotlib
```

### Development Dependencies

```bash
# Testing
uv pip install pytest pytest-cov

# Code quality
uv pip install black isort mypy

# Documentation
uv pip install sphinx mkdocs
```

### Optional Dependencies

```bash
# AI/ML packages
uv pip install scikit-learn torch

# Visualization
uv pip install plotly seaborn

# Web development
uv pip install flask fastapi
```

## 🚀 Advanced Patterns

### Conditional Installation

```bash
# Install based on environment
if ($env:ENVIRONMENT -eq "development") {
    uv pip install pytest black
} else {
    uv pip install gunicorn
}
```

### Batch Installation

```bash
# Install multiple packages
uv pip install numpy pandas matplotlib scikit-learn

# Install from file
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt
```

### Version Pinning

```bash
# Install specific versions
uv pip install numpy==1.24.0 pandas==2.0.0

# Install from constraints
uv pip install -c constraints.txt package-name
```

## 📝 Documentation Requirements

### Installation Documentation

````markdown
## Installation

This project uses UV cache for efficient package management.

### Prerequisites

- Python 3.11+
- UV package manager
- UV_CACHE_DIR environment variable set

### Setup

```bash
# Create venv
python -m venv .venv --symlinks

# Install dependencies
uv pip install -e .

# Run demo
uv run python demo_simple.py
```
````

````

### Code Comments
```python
# Installation - follows UV cache guidelines
# Dependencies installed via: uv pip install -e .
# Cache location: E:\uv-cache
# Venv size: < 100MB (mostly symlinks)
````

## 🎯 Success Criteria

### Installation Success

- [ ] Packages install from cache
- [ ] Venv remains minimal
- [ ] No network errors
- [ ] Import statements work
- [ ] Performance is fast

### Cache Efficiency

- [ ] Cache hits visible in output
- [ ] Install speed is fast
- [ ] Disk usage is minimal
- [ ] No duplicate packages

### Development Workflow

- [ ] Easy package addition
- [ ] Consistent environment
- [ ] Fast project setup
- [ ] Reliable builds

## 🚀 Benefits

### Why UV Installation Matters

1. **Speed**: 10x faster installs from cache
2. **Efficiency**: Minimal disk usage per project
3. **Reliability**: No network issues for cached packages
4. **Consistency**: Same packages across projects
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
- Keep venv minimal through cache
- Use project configuration

**NEVER**:

- Use `pip install` directly in venv
- Install packages globally
- Copy packages manually
- Ignore cache configuration

**RESULT**: Fast, efficient, minimal disk usage development environment.
