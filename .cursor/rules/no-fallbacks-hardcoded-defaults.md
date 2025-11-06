# No Fallbacks or Hardcoded Defaults Rule

## 🎯 Overview

**NEVER include fallbacks or hardcoded defaults** in code as they can cause hard-to-uncover errors and hide real problems. This rule ensures that errors are surfaced immediately rather than being masked by default values.

## 🚨 Why This Rule Exists

### Problems with Fallbacks and Defaults:

- **Hide Real Errors**: Mask underlying configuration or dependency issues
- **Silent Failures**: Code appears to work but produces incorrect results
- **Debugging Nightmare**: Hard to trace issues when defaults are applied
- **Inconsistent Behavior**: Different behavior in different environments
- **Security Risks**: Default values may be insecure or inappropriate

## ❌ Anti-Patterns (NEVER DO)

### ❌ Hardcoded Default Values

```python
# ❌ BAD - Hides configuration errors
def connect_to_api(api_url=None):
    if api_url is None:
        api_url = "http://localhost:3000"  # ❌ Hardcoded default
    return requests.get(api_url)

# ❌ BAD - Hides dependency issues
def load_font(font_path=None):
    if font_path is None:
        font_path = "Arial"  # ❌ Hardcoded fallback
    return font_path
```

### ❌ Silent Fallbacks

```python
# ❌ BAD - Silent fallback hides errors
def get_canvas_size(scene):
    try:
        return scene['canvas']['width'], scene['canvas']['height']
    except KeyError:
        return 1200, 630  # ❌ Silent fallback
```

### ❌ Configuration Defaults

```python
# ❌ BAD - Hardcoded configuration defaults
class LayoutEngine:
    def __init__(self, config=None):
        self.config = config or {
            'strategy': 'hero',  # ❌ Hardcoded default
            'timeout': 5000,      # ❌ Hardcoded default
            'cache_size': 1000    # ❌ Hardcoded default
        }

# ❌ BAD - Hardcoded values in code
def create_engine():
    return LayoutEngine({
        'strategy': 'hero',      # ❌ Hardcoded in code
        'timeout': 5000,         # ❌ Hardcoded in code
        'cache_size': 1000       # ❌ Hardcoded in code
    })
```

### ❌ Environment Fallbacks

```python
# ❌ BAD - Environment fallbacks hide setup issues
def get_cache_dir():
    cache_dir = os.environ.get('UV_CACHE_DIR')
    if not cache_dir:
        cache_dir = "E:\\uv-cache"  # ❌ Hardcoded fallback
    return cache_dir
```

## ✅ Correct Patterns (ALWAYS DO)

### ✅ Explicit Configuration Required

```python
# ✅ GOOD - Explicit configuration required
def connect_to_api(api_url: str):
    if not api_url:
        raise ValueError("API URL is required")
    return requests.get(api_url)

# ✅ GOOD - No fallbacks, fail fast
def load_font(font_path: str):
    if not font_path:
        raise ValueError("Font path is required")
    return font_path
```

### ✅ Fail Fast on Missing Data

```python
# ✅ GOOD - Fail fast, no silent fallbacks
def get_canvas_size(scene):
    canvas = scene.get('canvas')
    if not canvas:
        raise ValueError("Canvas configuration is required")

    width = canvas.get('width')
    height = canvas.get('height')

    if width is None or height is None:
        raise ValueError("Canvas width and height are required")

    return width, height
```

### ✅ Configuration Files

```python
# ✅ GOOD - Load configuration from file
import json
from pathlib import Path

def load_config(config_path: str) -> dict:
    """Load configuration from JSON file."""
    if not config_path:
        raise ValueError("Config file path is required")

    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, 'r') as f:
        config = json.load(f)

    # Validate required fields
    required_fields = ['strategy', 'timeout', 'cache_size']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Config file must contain '{field}' field")

    return config

# ✅ GOOD - Use config file instead of hardcoded values
def create_engine(config_path: str):
    config = load_config(config_path)
    return LayoutEngine(config)
```

### ✅ Explicit Configuration Objects

```python
# ✅ GOOD - Explicit configuration required
@dataclass
class LayoutConfig:
    strategy: str
    timeout: int
    cache_size: int

    def __post_init__(self):
        if not self.strategy:
            raise ValueError("Strategy is required")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.cache_size <= 0:
            raise ValueError("Cache size must be positive")

class LayoutEngine:
    def __init__(self, config: LayoutConfig):
        self.config = config
```

### ✅ Environment Validation

```python
# ✅ GOOD - Validate environment, fail if missing
def get_cache_dir():
    cache_dir = os.environ.get('UV_CACHE_DIR')
    if not cache_dir:
        raise EnvironmentError(
            "UV_CACHE_DIR environment variable is required. "
            "Set it with: setx UV_CACHE_DIR \"E:\\uv-cache\""
        )
    return cache_dir
```

## 🔧 Implementation Guidelines

### 1. **Configuration Validation**

```python
# ✅ GOOD - Validate all configuration
def validate_scene_config(scene):
    required_fields = ['canvas', 'elements']
    for field in required_fields:
        if field not in scene:
            raise ValueError(f"Scene must contain '{field}' field")

    canvas = scene['canvas']
    required_canvas_fields = ['width', 'height']
    for field in required_canvas_fields:
        if field not in canvas:
            raise ValueError(f"Canvas must contain '{field}' field")
```

### 2. **Dependency Validation**

```python
# ✅ GOOD - Validate dependencies exist
def validate_dependencies():
    try:
        import skia
        import yaml
        import requests
    except ImportError as e:
        raise ImportError(f"Required dependency missing: {e}")
```

### 3. **Environment Validation**

```python
# ✅ GOOD - Validate environment setup
def validate_environment():
    cache_dir = os.environ.get('UV_CACHE_DIR')
    if not cache_dir:
        raise EnvironmentError("UV_CACHE_DIR not set")

    if not os.path.exists(cache_dir):
        raise EnvironmentError(f"Cache directory does not exist: {cache_dir}")
```

### 4. **Input Validation**

```python
# ✅ GOOD - Validate all inputs
def process_scene(scene: dict, canvas: dict, options: dict):
    if not scene:
        raise ValueError("Scene is required")
    if not canvas:
        raise ValueError("Canvas is required")
    if not options:
        raise ValueError("Options are required")

    # Process with validated inputs
    return process_validated_scene(scene, canvas, options)
```

## 🎯 Error Handling Strategy

### 1. **Fail Fast Principle**

- **Validate early**: Check all requirements at startup
- **Fail immediately**: Don't continue with invalid configuration
- **Clear error messages**: Explain exactly what's missing
- **No silent failures**: Every error should be visible

### 2. **Configuration Requirements**

- **Use config files**: Load configuration from external files (JSON, YAML, etc.)
- **Explicit configuration**: All settings must be provided
- **No magic defaults**: Every value must be intentional
- **Validation required**: All inputs must be validated
- **Documentation required**: All requirements must be documented

### 3. **Error Messages**

```python
# ✅ GOOD - Clear, actionable error messages
def validate_api_config(api_url: str, api_key: str):
    if not api_url:
        raise ValueError(
            "API URL is required. "
            "Set it in your configuration or environment variables."
        )

    if not api_key:
        raise ValueError(
            "API key is required. "
            "Set it in your configuration or environment variables."
        )
```

## 📋 Checklist

### Before Writing Code

- [ ] **Use config files** - Load configuration from external files
- [ ] **No hardcoded defaults** - Every value must be explicit
- [ ] **No silent fallbacks** - All errors must be visible
- [ ] **Explicit validation** - All inputs must be validated
- [ ] **Clear error messages** - Errors must be actionable
- [ ] **Fail fast** - Errors must be caught early

### Code Review Checklist

- [ ] **Use config files** - Configuration loaded from external files
- [ ] **No `or` operators** for defaults (e.g., `value or "default"`)
- [ ] **No `get()` with defaults** (e.g., `dict.get('key', 'default')`)
- [ ] **No try/except with silent fallbacks**
- [ ] **No hardcoded configuration values**
- [ ] **No environment variable fallbacks**

## 🚨 Common Violations

### ❌ Violation Examples

```python
# ❌ VIOLATION - Hardcoded default
def get_timeout(config):
    return config.get('timeout', 5000)  # ❌ Hardcoded default

# ❌ VIOLATION - Silent fallback
def get_api_url():
    return os.environ.get('API_URL', 'http://localhost:3000')  # ❌ Fallback

# ❌ VIOLATION - Configuration default
def create_engine(config=None):
    config = config or {'strategy': 'hero'}  # ❌ Hardcoded default
```

### ✅ Corrected Examples

```python
# ✅ CORRECT - Explicit validation
def get_timeout(config):
    timeout = config.get('timeout')
    if timeout is None:
        raise ValueError("Timeout configuration is required")
    return timeout

# ✅ CORRECT - Explicit environment check
def get_api_url():
    api_url = os.environ.get('API_URL')
    if not api_url:
        raise EnvironmentError("API_URL environment variable is required")
    return api_url

# ✅ CORRECT - Explicit configuration
def create_engine(config):
    if not config:
        raise ValueError("Configuration is required")
    if 'strategy' not in config:
        raise ValueError("Strategy configuration is required")
```

## 🎯 Benefits

### Why This Rule Matters

1. **Immediate Error Detection**: Problems are caught early
2. **Clear Debugging**: Easy to identify what's missing
3. **Consistent Behavior**: Same behavior across environments
4. **Security**: No insecure defaults
5. **Maintainability**: Clear requirements and dependencies

### Development Benefits

- **Faster Debugging**: Errors are obvious, not hidden
- **Better Testing**: All edge cases are explicit
- **Clearer Documentation**: Requirements are explicit
- **Easier Deployment**: All configuration is explicit
- **Better Security**: No insecure defaults

## 🚀 Implementation

### Daily Practice

1. **Validate Everything**: Check all inputs and configuration
2. **Fail Fast**: Don't continue with invalid data
3. **Clear Errors**: Provide actionable error messages
4. **No Defaults**: Every value must be explicit
5. **Document Requirements**: Make all requirements clear

### Code Review

1. **Look for `or` operators**: These often indicate fallbacks
2. **Check `get()` calls**: Look for default values
3. **Review try/except**: Ensure errors are not silently caught
4. **Validate configuration**: Ensure all config is explicit
5. **Check environment**: Ensure all env vars are required

## 📚 Related Guidelines

- **[Path Guidelines](path-guidelines.md)** - Absolute path handling
- **[Installation Guidelines](installation-guidelines.md)** - Package management
- **[Code Reuse Guidelines](code-reuse-guidelines.md)** - Avoid file flooding
- **[Unicode Guidelines](unicode.mdc)** - ASCII-safe output

## 🎯 Summary

**ALWAYS**:

- Use config files for configuration
- Validate all inputs and configuration
- Fail fast with clear error messages
- Make all requirements explicit
- Document all dependencies
- Check environment setup

**NEVER**:

- Use hardcoded defaults
- Provide silent fallbacks
- Hide configuration errors
- Use `or` operators for defaults
- Catch exceptions silently
- Hardcode values in source code

**RESULT**: Robust, debuggable, and maintainable code with clear error handling.
