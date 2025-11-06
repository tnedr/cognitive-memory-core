# Code Reuse and File Management Guidelines

## 🎯 Overview

This document establishes guidelines for avoiding file flooding and promoting code reuse in the marketing pipeline project. The goal is to maintain a clean, organized codebase with minimal duplication and maximum reusability.

## 🚫 Avoid File Flooding

### ❌ DON'T Create New Files When Existing Ones Can Be Modified

```bash
# ❌ BAD - Creating multiple similar files
scripts/demo_basic.py
scripts/demo_advanced.py
scripts/demo_simple.py
scripts/demo_complex.py

# ✅ GOOD - Extending existing functionality
scripts/demo_full_pipeline.py  # Enhanced with new features
```

### ❌ DON'T Duplicate Functionality

```python
# ❌ BAD - Duplicate functions across files
# In file1.py
def validate_scene(scene):
    # validation logic

# In file2.py
def validate_scene_data(scene):
    # same validation logic
```

## ✅ Code Reuse Principles

### 1. **Check Before Creating**

Before creating any new file or function:

1. **Search existing codebase** for similar functionality
2. **Check if existing code can be extended**
3. **Look for reusable components**
4. **Consider refactoring existing code**

### 2. **Extend Before Duplicate**

```python
# ✅ GOOD - Extending existing functionality
# Original function
def render_scene(scene, output_path):
    # basic rendering

# Enhanced function (same file)
def render_scene(scene, output_path, scale=1, debug=False):
    # enhanced rendering with new parameters
```

### 3. **Modular Design**

```python
# ✅ GOOD - Modular, reusable components
# In utils/scene_utils.py
class SceneProcessor:
    def validate(self, scene): pass
    def render(self, scene, options): pass
    def analyze(self, scene): pass

# In different files
from utils.scene_utils import SceneProcessor
processor = SceneProcessor()
```

## 🔍 File Discovery Process

### Step 1: Search Before Create

```bash
# Search for existing functionality
grep -r "function_name" .
grep -r "class_name" .
grep -r "similar_keyword" .
```

### Step 2: Check Existing Structure

```bash
# Check existing file structure
ls scripts/
ls python-packages/
ls packages/
```

### Step 3: Analyze Reusability

- **Can existing code be extended?**
- **Can existing functions be parameterized?**
- **Can existing classes be inherited?**
- **Can existing modules be imported?**

## 📁 File Organization Rules

### ✅ GOOD File Organization

```
scripts/
├── demo_full_pipeline.py          # Main demo (extensible)
├── demo_executor.py               # Test executor
├── ai_analyzer.py                 # AI analysis
└── run_full_test.py               # Master test runner

python-packages/
├── py_visualizer/                 # Visual renderer
├── textpack_tools/                # TextPack utilities
└── shared_utils/                  # Shared utilities
```

### ❌ BAD File Organization

```
scripts/
├── demo1.py
├── demo2.py
├── demo3.py
├── test1.py
├── test2.py
├── test3.py
├── utils1.py
├── utils2.py
└── utils3.py
```

## 🔧 Refactoring Guidelines

### When to Refactor Instead of Create New

1. **Similar Functionality**: 80%+ overlap with existing code
2. **Same Purpose**: Same end goal as existing code
3. **Related Domain**: Same problem domain
4. **Shared Dependencies**: Uses same libraries/frameworks

### Refactoring Process

```python
# Step 1: Identify reusable parts
def existing_function(param1, param2):
    # common logic
    # specific logic

# Step 2: Extract common logic
def common_logic(param1):
    # common logic

def specific_logic(param2):
    # specific logic

# Step 3: Create reusable component
class ReusableComponent:
    def common_operation(self): pass
    def specific_operation(self): pass
```

## 🎯 Component Reuse Patterns

### 1. **Configuration Reuse**

```python
# ✅ GOOD - Shared configuration
# In project_config.py
DEFAULT_CONFIG = {
    'PROJECT_ROOT': str(PROJECT_ROOT),
    'PYTHON_PACKAGES_DIR': str(PROJECT_ROOT / 'python-packages'),
    # ... other config
}

# In multiple files
from project_config import DEFAULT_CONFIG
```

### 2. **Utility Function Reuse**

```python
# ✅ GOOD - Shared utilities
# In shared_utils.py
def validate_scene_structure(scene):
    # validation logic

def format_output_metrics(metrics):
    # formatting logic

# In multiple files
from shared_utils import validate_scene_structure, format_output_metrics
```

### 3. **Class Inheritance Reuse**

```python
# ✅ GOOD - Base class for reuse
class BaseAnalyzer:
    def __init__(self):
        self.results = {}

    def analyze(self):
        # common analysis logic
        pass

class VisualAnalyzer(BaseAnalyzer):
    def analyze(self):
        # visual-specific analysis
        super().analyze()
```

## 📊 File Count Guidelines

### Target Metrics

- **Scripts**: < 10 files (consolidate similar functionality)
- **Python Packages**: < 5 packages (group related functionality)
- **Documentation**: < 20 files (organize by topic)
- **Tests**: < 15 files (group by component)

### File Size Guidelines

- **Python Files**: < 500 lines (split if larger)
- **Documentation**: < 1000 lines (split if larger)
- **Configuration**: < 100 lines (keep minimal)

## 🔍 Code Discovery Tools

### Search Commands

```bash
# Search for existing functionality
grep -r "function_name" . --include="*.py"
grep -r "class_name" . --include="*.ts"
grep -r "keyword" . --include="*.md"

# Find similar files
find . -name "*demo*" -type f
find . -name "*test*" -type f
find . -name "*util*" -type f
```

### Analysis Commands

```bash
# Count files by type
find . -name "*.py" | wc -l
find . -name "*.ts" | wc -l
find . -name "*.md" | wc -l

# Find large files
find . -name "*.py" -exec wc -l {} + | sort -n
```

## 🚨 Anti-Patterns to Avoid

### ❌ File Flooding Anti-Patterns

```bash
# ❌ BAD - Too many similar files
demo_basic.py
demo_advanced.py
demo_simple.py
demo_complex.py
demo_test.py
demo_final.py

# ✅ GOOD - Consolidated approach
demo_full_pipeline.py  # With parameters for different modes
```

### ❌ Duplication Anti-Patterns

```python
# ❌ BAD - Duplicate logic
# In file1.py
def process_data(data):
    # processing logic

# In file2.py
def handle_data(data):
    # same processing logic
```

### ❌ Over-Engineering Anti-Patterns

```python
# ❌ BAD - Unnecessary abstraction
class DataProcessorFactory:
    def create_processor(self, type):
        if type == 'simple':
            return SimpleProcessor()
        elif type == 'complex':
            return ComplexProcessor()

# ✅ GOOD - Simple, direct approach
def process_data(data, options=None):
    # processing logic
```

## ✅ Best Practices

### 1. **Before Creating New File**

- [ ] Search existing codebase for similar functionality
- [ ] Check if existing code can be extended
- [ ] Consider if functionality belongs in existing file
- [ ] Evaluate if new file is truly necessary

### 2. **Before Creating New Function**

- [ ] Check if similar function already exists
- [ ] Consider if existing function can be parameterized
- [ ] Look for opportunities to extract common logic
- [ ] Ensure function has single responsibility

### 3. **Before Creating New Class**

- [ ] Check if similar class already exists
- [ ] Consider if existing class can be extended
- [ ] Look for opportunities to create base class
- [ ] Ensure class has clear purpose

### 4. **Code Review Checklist**

- [ ] No duplicate functionality
- [ ] Proper code organization
- [ ] Appropriate file count
- [ ] Clear naming conventions
- [ ] Good documentation

## 🎯 Success Metrics

### File Management Success

- ✅ **Low File Count**: Minimal number of files
- ✅ **High Reusability**: Maximum code reuse
- ✅ **Clear Organization**: Logical file structure
- ✅ **No Duplication**: No duplicate functionality
- ✅ **Easy Discovery**: Easy to find existing code

### Code Quality Success

- ✅ **Maintainable**: Easy to maintain and modify
- ✅ **Extensible**: Easy to extend existing functionality
- ✅ **Testable**: Easy to test individual components
- ✅ **Documented**: Clear documentation for all components
- ✅ **Consistent**: Consistent coding patterns

## 📚 Related Guidelines

- [Path Guidelines](path-guidelines.md) - Absolute path handling
- [Installation Guidelines](installation-guidelines.md) - Package management
- [Demo Execution Guidelines](demo-execution-guidelines.md) - Demo workflow
- [Unicode Guidelines](unicode.mdc) - ASCII-safe output

## 🚀 Implementation

### Daily Practice

1. **Search First**: Always search before creating
2. **Extend Second**: Extend existing code when possible
3. **Create Last**: Only create new when absolutely necessary
4. **Review Regularly**: Regular code review for file organization
5. **Refactor Often**: Refactor to improve reusability

### Weekly Practice

1. **File Audit**: Review file count and organization
2. **Duplication Check**: Look for duplicate functionality
3. **Refactoring Session**: Dedicated time for refactoring
4. **Documentation Update**: Update documentation for changes
5. **Team Review**: Team review of file organization

This ensures a clean, organized, and maintainable codebase with maximum code reuse! 🚀
