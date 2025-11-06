# Package Structure Guidelines

## 🎯 Standard Package Structure

> 🧭 **Repository Layout Note**
>
> This guide supports both **single-language** and **multi-language** repositories:
>
> - In **single-language** Python projects, use `packages/` as the root folder for all Python packages.
> - In **multi-language** monorepos (e.g., containing JavaScript, Go, or .NET), use `python-packages/` instead to clearly separate ecosystems.
>
> All examples below use `packages/` for simplicity, but the same structure applies under `python-packages/` when multiple languages are present.

### Repository Root Structure

```
repo_root/
├── packages/ or python-packages/  # All Python packages (depends on repo type)
│   ├── package_name/           # Individual package directory
│   │   ├── pyproject.toml      # Package-specific configuration
│   │   ├── src/                # Source code directory
│   │   │   └── package_name/   # Package source (same name as directory)
│   │   │       ├── __init__.py
│   │   │       ├── module1.py
│   │   │       └── module2.py
│   │   └── tests/              # Test directory
│   │       ├── __init__.py
│   │       ├── test_module1.py
│   │       └── test_module2.py
│   │
│   ├── another_package/        # Another package
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── another_package/
│   │   │       ├── __init__.py
│   │   │       └── main.py
│   │   └── tests/
│   │       └── test_main.py
│   │
│   └── shared_lib/             # Shared utilities
│       ├── pyproject.toml
│       ├── src/
│       │   └── shared_lib/
│       │       ├── __init__.py
│       │       └── utils.py
│       └── tests/
│           └── test_utils.py
│
├── pyproject.toml              # Root workspace configuration
└── README.md
```

## 📋 Package Structure Rules

### 1. Package Directory Naming

- **ALWAYS** use snake_case for package directory names
- **ALWAYS** match the package name with the source directory name
- **NEVER** use nested package names (e.g., `package_name/package_name/`)

### 2. Source Code Organization

```
packages/package_name/
├── pyproject.toml              # Package configuration
├── src/                        # Source code
│   └── package_name/           # Must match directory name
│       ├── __init__.py         # Package initialization
│       ├── main.py             # Main module
│       ├── utils.py            # Utility modules
│       └── submodule/          # Submodules (optional)
│           ├── __init__.py
│           └── helper.py
└── tests/                      # Test code
    ├── __init__.py
    ├── test_main.py
    ├── test_utils.py
    └── test_submodule/         # Test submodules (optional)
        ├── __init__.py
        └── test_helper.py
```

### 3. Required Files

#### Every Package Must Have:

- `pyproject.toml` - Package configuration
- `src/package_name/__init__.py` - Package initialization
- `tests/__init__.py` - Test package initialization

#### Optional Files:

- `README.md` - Package documentation
- `docs/` - Additional documentation
- `scripts/` - Utility scripts
- `examples/` - Usage examples

## 🔧 Implementation Guidelines

### 1. Package Configuration (pyproject.toml)

```toml
[build-system]
requires = ["hatchling>=1.25.0"]
build-backend = "hatchling.build"

[project]
name = "package-name"
version = "0.1.0"
description = "Package description"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "dependency1>=1.0.0",
    "dependency2>=2.0.0",
]

[project.scripts]
package-cli = "package_name.main:main"

[tool.hatch.build.targets.wheel]
packages = ["src/package_name"]
```

### 2. Package Initialization (src/package_name/**init**.py)

```python
"""Package Name

Short description of the package.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

# Import main functionality
from .main import main_function
from .utils import utility_function

__all__ = ["main_function", "utility_function"]
```

### 3. Test Structure

```python
# tests/test_main.py
import unittest
from package_name.main import main_function

class TestMain(unittest.TestCase):
    def test_main_function(self):
        result = main_function()
        self.assertIsNotNone(result)
```

## 🚫 Anti-Patterns (DO NOT USE)

### ❌ Wrong Package Structure

```
# WRONG - Nested package names
packages/package_name/
├── src/
│   └── package_name/           # ❌ Redundant nesting
│       └── package_name/       # ❌ Double nesting
│           └── __init__.py

# WRONG - No src directory
packages/package_name/
├── package_name/               # ❌ Source in root
│   └── __init__.py

# WRONG - Inconsistent naming
packages/my-package/            # ❌ Kebab case
├── src/
│   └── my_package/             # ❌ Snake case mismatch
```

### ❌ Wrong Import Patterns

```python
# WRONG - Relative imports in tests
from ..package_name.main import main_function

# WRONG - Manual path manipulation
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

## ✅ Correct Patterns

### ✅ Proper Package Structure

```
packages/cursor_agent_management/
├── pyproject.toml
├── src/
│   └── cursor_agent_management/
│       ├── __init__.py
│       ├── task_management.py
│       └── utils.py
└── tests/
    ├── __init__.py
    ├── test_task_management.py
    └── test_utils.py
```

### ✅ Correct Imports

```python
# In tests/test_task_management.py
import cursor_agent_management.task_management as tm

# In src/cursor_agent_management/__init__.py
from .task_management import main, load_tasks, save_tasks

# In other packages
from cursor_agent_management.task_management import main
```

## 🔧 Migration Checklist

When restructuring existing packages:

- [ ] Create `packages/` directory if it doesn't exist
- [ ] Move package to `packages/package_name/`
- [ ] Create `src/package_name/` directory
- [ ] Move source code to `src/package_name/`
- [ ] Create `tests/` directory
- [ ] Move tests to `tests/`
- [ ] Create `pyproject.toml` for the package
- [ ] Update imports in all files
- [ ] Update root `pyproject.toml` if needed
- [ ] Test that everything works

## 🎯 Benefits

### Why This Structure Matters

1. **Clarity**: Clear separation of source and test code
2. **Convention**: Follows Python packaging best practices
3. **Isolation**: Each package is self-contained
4. **Scalability**: Easy to add new packages
5. **Testing**: Clear test organization
6. **Distribution**: Easy to package and distribute

### Development Benefits

- **IDE Support**: Better autocomplete and navigation
- **Import Resolution**: Clear import paths
- **Testing**: Isolated test environments
- **Packaging**: Easy to build and distribute
- **Documentation**: Clear structure for docs

## 📚 Examples

### Example 1: Simple Package

```
packages/calculator/
├── pyproject.toml
├── src/
│   └── calculator/
│       ├── __init__.py
│       ├── basic.py
│       └── advanced.py
└── tests/
    ├── test_basic.py
    └── test_advanced.py
```

### Example 2: Complex Package

```
packages/web_scraper/
├── pyproject.toml
├── README.md
├── src/
│   └── web_scraper/
│       ├── __init__.py
│       ├── scraper.py
│       ├── parser.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── test_scraper.py
│   ├── test_parser.py
│   └── test_utils/
│       └── test_helpers.py
└── docs/
    └── API.md
```

## 🚀 Implementation

### Step 1: Create Package Structure

```bash
mkdir -p packages/package_name/src/package_name
mkdir -p packages/package_name/tests
```

### Step 2: Create Required Files

```bash
# Create __init__.py files
touch packages/package_name/src/package_name/__init__.py
touch packages/package_name/tests/__init__.py

# Create pyproject.toml
touch packages/package_name/pyproject.toml
```

### Step 3: Move Source Code

```bash
# Move existing code
mv existing_code.py packages/package_name/src/package_name/
mv existing_tests.py packages/package_name/tests/
```

### Step 4: Update Imports

```python
# Update all import statements
# From: from old_module import function
# To:   from package_name.module import function
```

## 🎯 Summary

**ALWAYS**:

- Use `packages/package_name/src/package_name/` structure
- Match directory and package names
- Separate source and test code
- Use proper `pyproject.toml` configuration
- Follow Python packaging conventions

**NEVER**:

- Use nested package names
- Mix source and test code
- Use inconsistent naming
- Skip package configuration
- Ignore import structure

**RESULT**: Clean, maintainable, and scalable package structure.

## 🧩 Workspace Integration (Recommended for Monorepos)

In multi-package repositories, define a workspace in the root `pyproject.toml`:

```toml
[project]
name = "the-factory-monorepo"
version = "0.1.0"

[tool.uv.workspace]
```

This allows:

- All sub-packages under `packages/` or `python-packages/` to be discovered automatically.
- A single `.venv` in the repo root to serve all packages.
- Shared dependencies and testing across packages.
