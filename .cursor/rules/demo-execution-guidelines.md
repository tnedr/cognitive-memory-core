# Demo Execution Guidelines

## 🎯 Overview

This document defines the standardized approach for executing demos in the marketing pipeline project. All demo executions must follow these guidelines to ensure consistency, reliability, and proper dependency management.

## 🚀 Demo Execution Rules

### ✅ ALWAYS Use UV for Python Execution

#### ❌ WRONG - Direct Python Execution

```bash
# NEVER do this
python scripts/demo_full_pipeline.py
python scripts/demo_executor.py
python scripts/ai_analyzer.py
```

#### ✅ CORRECT - UV Execution

```bash
# ALWAYS use uv run
uv run python scripts/demo_full_pipeline.py
uv run python scripts/demo_executor.py
uv run python scripts/ai_analyzer.py
```

### 🎯 Why UV Execution is Required

1. **Dependency Management**: UV ensures all dependencies are available
2. **Virtual Environment**: Automatic venv activation and management
3. **Cache Optimization**: Uses global UV cache for fast installs
4. **Consistency**: Same environment across all executions
5. **Error Prevention**: Avoids "module not found" errors

## 📋 Demo Execution Workflow

### 1. Standard Demo Execution

```bash
# Basic demo with fallback scene
uv run python scripts/demo_full_pipeline.py
```

### 2. Comprehensive Testing

```bash
# Full test suite with AI analysis
uv run python scripts/run_full_test.py
```

### 3. Individual Component Testing

```bash
# Test demo execution only
uv run python scripts/demo_executor.py

# Run AI analysis on results
uv run python scripts/ai_analyzer.py
```

## 🔧 Pre-Execution Checklist

### Before Running Any Demo

1. **Check UV Cache Status**

   ```bash
   uv cache dir
   # Should show: E:\uv-cache
   ```

2. **Verify Dependencies**

   ```bash
   uv pip list | findstr skia
   uv pip list | findstr pyyaml
   uv pip list | findstr requests
   ```

3. **Check Project Structure**
   ```bash
   # Ensure you're in project root
   echo (Get-Location).Path
   # Should show: E:\Repos\marketing-pipeline
   ```

## 🎨 Demo Types and Commands

### 1. Basic Demo (Recommended)

```bash
# Simple demo with local scene builder
uv run python scripts/demo_full_pipeline.py
```

**Output**: `full_pipeline.png` (1080×1350)

### 2. API Demo (When Orchestrator Running)

```bash
# Terminal 1: Start orchestrator
cd packages/orchestrator && bun dev

# Terminal 2: Run demo with API
uv run python scripts/demo_full_pipeline.py
```

### 3. Comprehensive Testing

```bash
# Full test suite with logging and AI analysis
uv run python scripts/run_full_test.py
```

**Output**: `demo_logs/` directory with detailed results

### 4. Individual Testing

```bash
# Test specific components
uv run python scripts/demo_executor.py    # Test execution
uv run python scripts/ai_analyzer.py      # Analyze results
```

## 📊 Expected Outputs

### Successful Demo Execution

```
Starting end-to-end demo pipeline...
INFO: Using local scene builder (API not available)
Rendering scene to PNG...
SUCCESS: Rendered full_pipeline.png (1080x1350px)
Objects: 10
Warnings: 0
File size: 77,938 bytes
```

### Successful Test Execution

```
AI Analyzer - Analyzing demo execution results...
Overall Status: EXCELLENT
Quality Score: 85.0/100
Analysis saved to: demo_logs/ai_analysis_20250110_104530.json
```

## 🚨 Error Handling

### Common Issues and Solutions

#### 1. Module Not Found

```bash
# ERROR: ModuleNotFoundError: No module named 'skia'
# SOLUTION: Use uv run instead of python
uv run python scripts/demo_full_pipeline.py
```

#### 2. API Connection Failed

```bash
# ERROR: API not available
# SOLUTION: Use standalone mode (automatic fallback)
uv run python scripts/demo_full_pipeline.py
```

#### 3. Path Issues

```bash
# ERROR: File not found
# SOLUTION: Ensure you're in project root
echo (Get-Location).Path
cd E:\Repos\marketing-pipeline
```

#### 4. Unicode Issues

```bash
# ERROR: UnicodeEncodeError: 'charmap' codec can't encode character
# SOLUTION: Use ASCII-safe output in all Python scripts
# See: .cursor/rules/unicode.mdc for detailed guidelines
```

## 📁 Output Structure

### Demo Outputs

```
E:\Repos\marketing-pipeline\
├── full_pipeline.png          # Generated image
├── demo_logs/                 # Test results
│   ├── demo_20250110_104530.log
│   ├── demo_20250110_104530_results.json
│   └── ai_analysis_20250110_104530.json
└── scripts/                   # Demo scripts
    ├── demo_full_pipeline.py
    ├── demo_executor.py
    ├── ai_analyzer.py
    └── run_full_test.py
```

## 🎯 Quality Standards

### Demo Success Criteria

- [ ] **Execution**: No errors during execution
- [ ] **Output**: PNG file generated successfully
- [ ] **Quality**: File size between 20KB-200KB
- [ ] **Content**: Multiple visual elements rendered
- [ ] **Performance**: Execution time < 30 seconds

### Test Success Criteria

- [ ] **API Test**: API available or graceful fallback
- [ ] **Demo Test**: Successful PNG generation
- [ ] **Quality Test**: Output file meets standards
- [ ] **Visual Test**: No rendering warnings
- [ ] **AI Analysis**: Quality score > 60%

## 🔄 Workflow Integration

### Development Workflow

1. **Make Changes**: Modify demo scripts or scenes
2. **Test Changes**: `uv run python scripts/demo_full_pipeline.py`
3. **Verify Quality**: `uv run python scripts/run_full_test.py`
4. **Check Results**: Review `demo_logs/` directory

### CI/CD Integration

```bash
# Automated testing in CI/CD
uv run python scripts/run_full_test.py
# Exit code 0 = success, 1 = failure
```

## 📚 Documentation References

### Related Guidelines

- [Installation Guidelines](installation-guidelines.md) - UV-first package management
- [UV Cache Workflow](uv-cache-workflow.md) - Efficient caching strategies
- [Path Guidelines](path-guidelines.md) - Absolute path handling
- [Unicode Guidelines](unicode.mdc) - ASCII-safe output for Windows compatibility
- [Troubleshooting Guide](../docs/troubleshooting.md) - Common issues and solutions

### Demo Documentation

- [Demo Full Workflow](../docs/python/demo_full_workflow.md) - Complete workflow guide
- [Scene YAML Examples](../docs/scene-yaml-examples.md) - Scene specification
- [Scene YAML Quick Reference](../docs/scene-yaml-quick-reference.md) - Quick reference

## 🎉 Best Practices

### ✅ DO

- Always use `uv run python` for execution
- Check UV cache status before running
- Use comprehensive testing for important changes
- Review AI analysis results for quality insights
- Keep demo outputs in version control (when appropriate)

### ❌ DON'T

- Use direct `python` execution
- Skip dependency checks
- Ignore error messages
- Run demos without proper environment setup
- Forget to check output quality
- Use Unicode characters in Python output (causes Windows terminal errors)
- Use emojis in print statements
- Use special Unicode symbols (✓, ✗, 🚀, etc.)

## 🚀 Quick Commands Reference

### Essential Commands

```bash
# Basic demo
uv run python scripts/demo_full_pipeline.py

# Full testing
uv run python scripts/run_full_test.py

# Check UV cache
uv cache dir

# Check dependencies
uv pip list | findstr skia
```

### Troubleshooting Commands

```bash
# Check project structure
echo (Get-Location).Path
ls scripts/

# Check demo logs
ls demo_logs/

# Verify output
ls full_pipeline.png
```

## 🎯 Success Metrics

### Demo Execution Success

- ✅ **Zero Errors**: No Python exceptions
- ✅ **File Generated**: PNG output created
- ✅ **Reasonable Size**: 20KB-200KB file size
- ✅ **Fast Execution**: < 30 seconds
- ✅ **Rich Content**: 5+ visual elements

### Test Suite Success

- ✅ **All Tests Pass**: 100% success rate
- ✅ **Quality Score**: > 60% AI analysis score
- ✅ **No Warnings**: Clean execution
- ✅ **Proper Logging**: Detailed logs generated
- ✅ **AI Insights**: Actionable recommendations

This ensures consistent, reliable demo execution across the entire project! 🚀
