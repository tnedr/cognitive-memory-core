# Centralized Path Management Rules

## 🎯 Overview

This project uses a centralized path management system for all Python imports and file operations. All AI coders must follow these principles to maintain consistency and avoid import issues.

## 📋 Core Principles

### 1. ALWAYS Use Centralized Path Management

- **NEVER** use `sys.path.insert()` or manual path manipulation
- **NEVER** use relative imports like `from .module import something`
- **ALWAYS** use the centralized `path_manager.py` system

### 2. Required Import Pattern

```python
# ALWAYS start Python files with these imports
from path_manager import path_manager, setup_environment

# Set up environment and paths
setup_environment()
path_manager._setup_python_path()
```

### 3. Absolute Import Rules

- **ALWAYS** use absolute imports with package prefixes
- **NEVER** use relative imports within the project
- **ALWAYS** prefix with the package name

#### ✅ CORRECT Import Patterns:

```python
# Py-visualizer imports
from py_visualizer.parser import parse_scene_spec, load_scene_from_file
from py_visualizer.render import render_scene_to_png
from py_visualizer.layout import LayoutEngine
from py_visualizer.text import TextMeasurer
from py_visualizer.image import ImageLoader, compute_object_fit
from py_visualizer.font import FontManager
from py_visualizer.spec_types import Scene, Layout, Metrics

# Scripts imports (when available)
from scripts.demo_executor import DemoExecutor
from scripts.ai_analyzer import AIAnalyzer
```

#### ❌ WRONG Import Patterns:

```python
# NEVER do this - relative imports
from .parser import parse_scene_spec
from ..layout import LayoutEngine

# NEVER do this - manual path manipulation
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# NEVER do this - direct imports without package prefix
from parser import parse_scene_spec
from layout import LayoutEngine
```

### 4. File Path Operations

- **ALWAYS** use `path_manager` for file paths
- **NEVER** hardcode paths or use relative paths
- **ALWAYS** use absolute paths from the path manager

#### ✅ CORRECT Path Usage:

```python
from path_manager import path_manager

# Get project paths
project_root = path_manager.project_root
py_visualizer_dir = path_manager.py_visualizer
scripts_dir = path_manager.scripts
docs_dir = path_manager.docs

# Create file paths
output_file = path_manager.project_root / "output.png"
config_file = path_manager.config / "settings.yaml"

# Ensure directories exist
path_manager.ensure_directory(path_manager.get_temp_dir() / "demo")
```

#### ❌ WRONG Path Usage:

```python
# NEVER hardcode paths
output_file = Path("output.png")
config_file = Path("../config/settings.yaml")

# NEVER use relative paths
output_file = Path(__file__).parent / "output.png"
```

### 5. Test Files

- **ALWAYS** use the centralized path system in tests
- **NEVER** use `sys.path.insert()` in test files
- **ALWAYS** import test utilities through the path manager

#### ✅ CORRECT Test Pattern:

```python
import pytest
from path_manager import path_manager

# Set up paths
path_manager._setup_python_path()

# Import modules under test
from py_visualizer.parser import parse_scene_spec
from py_visualizer.layout import LayoutEngine
```

### 6. Script Files

- **ALWAYS** use centralized path management in scripts
- **NEVER** use old `project_config.py` or `path_utils.py`
- **ALWAYS** use the new `path_manager.py` system

#### ✅ CORRECT Script Pattern:

```python
#!/usr/bin/env python3
"""
Script description
"""

# Import centralized path management
from path_manager import path_manager, setup_environment

# Set up environment and paths
setup_environment()
path_manager._setup_python_path()

# Now use absolute imports
from py_visualizer.render import render_scene_to_png
```

## 🚫 Forbidden Patterns

### 1. Manual Path Manipulation

```python
# ❌ NEVER do this
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### 2. Relative Imports

```python
# ❌ NEVER do this
from .module import function
from ..package.module import function
```

### 3. Direct Imports Without Package Prefix

```python
# ❌ NEVER do this
from parser import parse_scene_spec
from layout import LayoutEngine
```

### 4. Hardcoded Paths

```python
# ❌ NEVER do this
output_path = "output.png"
config_path = "../config/settings.yaml"
```

## ✅ Required File Structure

### Every Python File Must Start With:

```python
#!/usr/bin/env python3
"""
File description
"""

# Standard library imports first
import os
import sys
from pathlib import Path

# Import centralized path management
from path_manager import path_manager, setup_environment

# Set up environment and paths
setup_environment()
path_manager._setup_python_path()

# Now use absolute imports
from py_visualizer.module_name import function_name
```

## 🔧 Migration Checklist

When updating existing files:

- [ ] Remove all `sys.path.insert()` calls
- [ ] Remove all relative imports
- [ ] Add centralized path management imports
- [ ] Convert to absolute imports with package prefixes
- [ ] Replace hardcoded paths with `path_manager` references
- [ ] Test that imports work correctly

## 📚 Reference Files

- **Path Manager**: `python-packages/path_manager.py`
- **Import Utils**: `python-packages/import_utils.py`
- **Migration Guide**: `python-packages/MIGRATION_GUIDE.md`
- **Example Usage**: `python-packages/example_usage.py`
- **Test Suite**: `python-packages/test_paths.py`

## 🎯 Benefits

1. **Consistent Imports**: All files use the same import pattern
2. **Better IDE Support**: IDEs can properly resolve imports
3. **Easier Debugging**: Import errors are clearer
4. **Future-Proof**: Adding new modules is easier
5. **No Path Issues**: Centralized path management prevents path-related bugs

## ⚠️ Important Notes

- **ALWAYS** test imports after making changes
- **ALWAYS** use the test suite to validate the system
- **NEVER** mix old and new import patterns in the same file
- **ALWAYS** update all imports when restructuring modules

## 🧪 Testing

Run the test suite to validate the system:

```bash
python python-packages/test_paths.py
```

This will verify that:

- Path manager is working correctly
- Import utils are functioning
- Python path is set up properly
- Absolute imports work correctly
