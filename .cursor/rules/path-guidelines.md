# Path Guidelines for Marketing Pipeline

## 🎯 Project Structure Principles

### Absolute Paths Everywhere

- **NEVER** use relative paths in production code
- **ALWAYS** use absolute paths with proper path handling
- **CONSISTENT** path resolution across all components

### Path Resolution Hierarchy

1. **Environment Variables** (highest priority)
2. **Project Configuration** (fallback)
3. **Default Paths** (last resort)

## 📁 Standard Project Paths

### Core Directories

```python
PROJECT_ROOT = "E:\\Repos\\marketing-pipeline"
PYTHON_PACKAGES_DIR = "E:\\Repos\\marketing-pipeline\\python-packages"
SCRIPTS_DIR = "E:\\Repos\\marketing-pipeline\\scripts"
DOCS_DIR = "E:\\Repos\\marketing-pipeline\\docs"
```

### Package-Specific Paths

```python
PY_VISUALIZER_DIR = "E:\\Repos\\marketing-pipeline\\python-packages\\py_visualizer"
AI_SERVICES_DIR = "E:\\Repos\\marketing-pipeline\\python-packages\\ai-services"
```

### Cache and Temporary Paths

```python
UV_CACHE_DIR = "E:\\uv-cache"
TEMP_DIR = "E:\\DevSSD\\temp"
TMP_DIR = "E:\\DevSSD\\temp"
```

## 🔧 Path Handling Implementation

### Required Pattern

```python
# ALWAYS use this pattern for path handling
from path_manager import setup_environment, get_project_root, get_python_packages_dir

# Set up environment first
setup_environment()

# Use absolute paths
project_root = get_project_root()
python_packages = get_python_packages_dir()
```

### Path Utilities

```python
# Use unified path_manager.py for all path operations
from path_manager import get_py_visualizer_dir, get_hybrid_layout_dir, setup_environment

# Set up environment and Python path
setup_environment()
py_visualizer_path = get_py_visualizer_dir()
hybrid_layout_path = get_hybrid_layout_dir()
```

## 🚫 Anti-Patterns (DO NOT USE)

### ❌ Relative Paths

```python
# WRONG - Never do this
sys.path.insert(0, 'python-packages/py-visualizer')
import py_visualizer
```

### ❌ Hardcoded Paths

```python
# WRONG - Never hardcode paths
py_visualizer_path = "E:\\Repos\\marketing-pipeline\\python-packages\\py-visualizer"
```

### ❌ Manual Path Construction

```python
# WRONG - Don't construct paths manually
import os
path = os.path.join(os.getcwd(), "python-packages", "py-visualizer")
```

## ✅ Correct Patterns

### ✅ Environment-Based Paths

```python
# CORRECT - Use unified path manager
from path_manager import get_py_visualizer_dir
py_visualizer_path = get_py_visualizer_dir()
```

### ✅ Configuration-Driven Paths

```python
# CORRECT - Use unified path manager
from path_manager import setup_environment, get_project_root
setup_environment()
project_root = get_project_root()
```

### ✅ Path Utilities

```python
# CORRECT - Use unified path manager
from path_manager import setup_environment, get_py_visualizer_dir
setup_environment()
py_visualizer_dir = get_py_visualizer_dir()
```

## 🔍 Path Validation

### Always Validate Paths

```python
from pathlib import Path

def validate_path(path: Path) -> bool:
    """Validate that a path exists and is accessible."""
    return path.exists() and path.is_dir()

# Use in code
py_visualizer_dir = get_py_visualizer_dir()
if not validate_path(py_visualizer_dir):
    raise FileNotFoundError(f"Path not found: {py_visualizer_dir}")
```

### Path Debugging

```python
# Use this for debugging path issues
from path_manager import print_project_info
print_project_info()
```

## 📋 Path Checklist

### Before Using Any Path

- [ ] Is it using absolute paths?
- [ ] Is it using project configuration?
- [ ] Is it validated before use?
- [ ] Is it environment-variable driven?
- [ ] Is it documented in this file?

### Path Implementation

- [ ] Import `path_manager` (unified path management)
- [ ] Call `setup_environment()` first
- [ ] Use provided path functions
- [ ] Validate paths before use
- [ ] Handle path errors gracefully

## 🎯 Benefits

### Why These Guidelines Matter

1. **Portability**: Works on any system with proper environment setup
2. **Maintainability**: Single source of truth for all paths
3. **Debugging**: Easy to trace path issues
4. **Consistency**: Same path handling everywhere
5. **Flexibility**: Easy to change paths via environment variables

## 🚀 Implementation Examples

### Demo Scripts

```python
# demo_simple.py - CORRECT implementation
from path_manager import setup_environment, get_py_visualizer_dir
import sys

# Set up environment
setup_environment()

# Add to Python path
py_visualizer_path = str(get_py_visualizer_dir())
if py_visualizer_path not in sys.path:
    sys.path.insert(0, py_visualizer_path)

# Now import works
from py_visualizer import render_scene_to_png
```

### Package Imports

```python
# Any Python file - CORRECT implementation
from path_manager import setup_environment
setup_environment()

# Now all imports work with absolute paths
from py_visualizer import render_scene_to_png
from ai_services import openai_client
```

## 🔧 Environment Setup

### Required Environment Variables

```bash
# Set these in your environment or .env file
PROJECT_ROOT=E:\Repos\marketing-pipeline
PYTHON_PACKAGES_DIR=E:\Repos\marketing-pipeline\python-packages
PY_VISUALIZER_DIR=E:\Repos\marketing-pipeline\python-packages\py_visualizer
UV_CACHE_DIR=E:\uv-cache
```

### Python Path Setup

```python
# Always call this at the start of any script
from path_manager import setup_environment
setup_environment()
```

## 📝 Documentation Requirements

### Path Documentation

- Document all custom path functions
- Explain path resolution logic
- Provide usage examples
- Include troubleshooting steps

### Code Comments

```python
# Path handling - follows project guidelines
from path_manager import setup_environment, get_py_visualizer_dir

# Set up environment for absolute path resolution
setup_environment()

# Get absolute path to py-visualizer package
py_visualizer_dir = get_py_visualizer_dir()
```

## 🎯 Summary

**ALWAYS**:

- Use absolute paths
- Use project configuration
- Validate paths
- Handle errors gracefully
- Document path usage

**NEVER**:

- Use relative paths
- Hardcode paths
- Construct paths manually
- Skip path validation
- Ignore path errors
