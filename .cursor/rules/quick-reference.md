# Quick Reference Card

## 🚀 Essential Commands

### Demo Execution

```bash
# Basic demo
uv run python scripts/demo_full_pipeline.py

# Complete testing
uv run python scripts/run_full_test.py

# Individual testing
uv run python scripts/demo_executor.py
uv run python scripts/ai_analyzer.py
```

### Status Checks

```bash
# Check project location
echo (Get-Location).Path

# Check UV cache
uv cache dir

# Check dependencies
uv pip list | findstr skia
```

## ⚡ Core Rules

### 1. **ALWAYS Use UV**

```bash
# ✅ CORRECT
uv run python scripts/demo_full_pipeline.py

# ❌ NEVER
python scripts/demo_full_pipeline.py
```

### 2. **ASCII-Safe Output**

```python
# ✅ CORRECT
print("SUCCESS: Operation completed")
print("+ Check passed")

# ❌ NEVER
print("✅ Success!")
print("✓ Check passed")
```

### 3. **Absolute Paths**

```python
# ✅ CORRECT
from project_config import setup_environment
setup_environment()

# ❌ NEVER
sys.path.append('python-packages/py-visualizer')
```

## 🎯 Success Criteria

### Demo Success

- ✅ No Python errors
- ✅ PNG file generated (20KB-200KB)
- ✅ 5+ visual elements
- ✅ < 30 seconds execution
- ✅ No rendering warnings

### Test Success

- ✅ All tests pass (100%)
- ✅ Quality score > 60%
- ✅ No Unicode errors
- ✅ Output files generated
- ✅ Performance within limits

## 🚨 Common Issues

### Module Not Found

```bash
# ERROR: ModuleNotFoundError
# SOLUTION: Use uv run instead of python
uv run python scripts/demo_full_pipeline.py
```

### Unicode Errors

```bash
# ERROR: UnicodeEncodeError
# SOLUTION: Use ASCII-safe output
# See: unicode.mdc for details
```

### API Issues

```bash
# ERROR: API not available
# SOLUTION: Use standalone mode (automatic fallback)
uv run python scripts/demo_full_pipeline.py
```

## 📁 Key Files

- **`scripts/demo_full_pipeline.py`** - Main demo
- **`scripts/run_full_test.py`** - Complete testing
- **`project_config.py`** - Path configuration
- **`demo_logs/`** - Test results
- **`.cursor/rules/agents.md`** - Master guide

## 🔧 Troubleshooting

### Check Project Status

```bash
echo (Get-Location).Path
uv cache dir
ls scripts/
```

### Check Demo Results

```bash
ls demo_logs/
ls full_pipeline.png
```

### Verify Dependencies

```bash
uv pip list | findstr skia
uv pip list | findstr pyyaml
uv pip list | findstr requests
```

## 📚 Full Documentation

- **[agents.md](agents.md)** - Complete agent guide
- **[demo-execution-guidelines.md](demo-execution-guidelines.md)** - Demo workflow
- **[code-reuse-guidelines.md](code-reuse-guidelines.md)** - Avoid file flooding and promote code reuse
- **[unicode.mdc](unicode.mdc)** - Unicode guidelines
- **[installation-guidelines.md](installation-guidelines.md)** - Package management
- **[path-guidelines.md](path-guidelines.md)** - Path handling
