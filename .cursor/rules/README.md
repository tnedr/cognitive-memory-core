# Marketing Pipeline - Cursor Rules

This directory contains comprehensive development guidelines for the Marketing Pipeline project.

## 🎯 **START HERE: Master Agent Guide**

**[agents.md](agents.md)** - **Complete guide for Cursor agents working on this project**

- Quick start commands
- Core rules summary
- Demo execution workflow
- Package management
- Quality standards
- Common issues & solutions
- Development workflow
- Best practices

## ⚡ **Quick Reference**

**[quick-reference.md](quick-reference.md)** - **Essential commands and rules at a glance**

- Essential commands
- Core rules
- Success criteria
- Common issues
- Troubleshooting

## 📋 Available Guidelines

### 🛠️ Development Workflow

- **[Path Guidelines](path-guidelines.md)** - Absolute path handling and project structure
- **[UV Cache Workflow](uv-cache-workflow.md)** - Efficient package management with uv cache
- **[Installation Guidelines](installation-guidelines.md)** - UV-first package installation patterns
- **[Demo Execution Guidelines](demo-execution-guidelines.md)** - Standardized demo execution with UV
- **[Code Reuse Guidelines](code-reuse-guidelines.md)** - Avoid file flooding and promote code reuse
- **[No Fallbacks Rule](no-fallbacks-hardcoded-defaults.md)** - Avoid fallbacks and hardcoded defaults
- **[PowerShell Windows](powershell-windows.mdc)** - Windows PowerShell best practices
- **[Unicode Guidelines](unicode.mdc)** - Unicode and encoding best practices

### 🤖 AI Agent System

- **[Agent System](../agents/README.md)** - Specialized AI agents for on-demand expertise
- **[Agent Invocation](../agents/agent-invocation.md)** - How to use and switch between agents

## 🎯 Quick Reference

### Path Handling

```python
# ALWAYS use this pattern
from project_config import setup_environment, get_py_visualizer_dir
setup_environment()
py_visualizer_dir = get_py_visualizer_dir()
```

### UV Cache Usage

```bash
# ALWAYS use uv for package management
uv pip install -e .
uv run python script.py
```

### Package Installation

```bash
# ALWAYS use uv pip install
uv pip install skia-python pyyaml requests
uv pip install -e .[dev,test]
```

### PowerShell Commands

```powershell
# ALWAYS use these reliable commands
echo (Get-Location).Path
Write-Host "Output message"
```

### Unicode Safety

```python
# ALWAYS use ASCII-safe output
print("SUCCESS: Operation completed")
print("ERROR: Operation failed")
```

## 🚀 Getting Started

### 1. Set Up Environment

```bash
# Set UV cache location
setx UV_CACHE_DIR "E:\uv-cache"

# Create minimal venv
python -m venv .venv --symlinks

# Install dependencies
uv pip install -e .
```

### 2. Run Demo

```bash
# Set up paths and run demo
python demo_simple.py
```

### 3. Verify Setup

```bash
# Check cache is working
uv cache dir
# Should show: E:\uv-cache

# Check venv is minimal
Get-ChildItem .venv -Recurse | Measure-Object -Property Length -Sum
# Should be < 100MB
```

## 📝 Rule Categories

### 🔧 Technical Rules

- **Path Guidelines**: Absolute paths, environment variables, project structure
- **UV Cache**: Package management, cache optimization, minimal venv
- **No Fallbacks**: Avoid fallbacks and hardcoded defaults, fail fast
- **PowerShell**: Windows terminal compatibility, reliable commands
- **Unicode**: ASCII-safe output, Windows compatibility

### 🎯 Development Rules

- **Code Quality**: Consistent patterns, error handling, documentation
- **Performance**: Fast installs, minimal disk usage, efficient workflows
- **Maintainability**: Clear structure, documented patterns, easy debugging

### 🚀 Workflow Rules

- **Setup**: Environment configuration, path resolution, cache setup
- **Development**: Daily workflow, package management, testing
- **Deployment**: CI/CD compatibility, production readiness

## 🔍 Troubleshooting

### Common Issues

1. **Path Issues**: Check `project_config.py` and environment variables
2. **Cache Issues**: Verify `UV_CACHE_DIR` and run `uv cache dir`
3. **Import Issues**: Ensure `setup_environment()` is called first
4. **PowerShell Issues**: Use `Write-Host` instead of `print` for output

### Debug Commands

```bash
# Check project configuration
python project_config.py

# Check path setup
python python-packages/path_utils.py

# Check cache status
uv cache dir
uv cache info
```

## 📊 Quality Metrics

### Path Handling

- ✅ All paths are absolute
- ✅ Environment variables used
- ✅ Path validation implemented
- ✅ Error handling present

### UV Cache

- ✅ Global cache configured
- ✅ Minimal venv size
- ✅ Fast package installs
- ✅ Cache hits visible

### PowerShell

- ✅ Reliable commands used
- ✅ ASCII-safe output
- ✅ Windows compatible
- ✅ Error handling present

## 🎯 Success Criteria

### Development Environment

- [ ] UV cache working (`E:\uv-cache`)
- [ ] Minimal venv (< 100MB)
- [ ] Fast package installs
- [ ] Absolute paths everywhere
- [ ] Environment variables set
- [ ] PowerShell commands working
- [ ] Unicode-safe output
- [ ] Demo scripts running

### Code Quality

- [ ] Path guidelines followed
- [ ] UV cache used correctly
- [ ] PowerShell compatibility
- [ ] Unicode safety maintained
- [ ] Error handling present
- [ ] Documentation complete

## 📚 Additional Resources

### Documentation

- [Project README](../README.md)
- [Development Guidelines](../docs/guidelines/)
- [Python Documentation](../docs/python/)

### Configuration Files

- [pyproject.toml](../pyproject.toml) - Project dependencies
- [project_config.py](../project_config.py) - Path configuration
- [.gitignore](../.gitignore) - Git ignore rules

### Demo Scripts

- [demo_simple.py](../demo_simple.py) - Basic demo
- [scripts/](../scripts/) - Demo scripts directory

## 🚀 Next Steps

1. **Read the guidelines** in each rule file
2. **Set up your environment** following the workflow
3. **Run the demo** to verify everything works
4. **Follow the patterns** in your own code
5. **Contribute improvements** to the guidelines

---

**Remember**: These rules ensure consistent, efficient, and maintainable development across the entire Marketing Pipeline project.
