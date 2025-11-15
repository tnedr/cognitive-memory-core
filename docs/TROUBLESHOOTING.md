# Troubleshooting Guide

## Common Issues and Solutions

### 1. Search Returns "No results found"

**Symptom:**
```bash
uv run cmemory search "your query"
# Output: No results found
```

**Cause:** Dummy embeddings are being used because `sentence-transformers` is not properly installed or has dependency conflicts.

**Solution:**

1. **Install sentence-transformers:**
   ```bash
   uv pip install sentence-transformers
   ```

2. **If you see dependency conflicts:**
   ```bash
   # Try reinstalling with compatible versions
   uv pip install "sentence-transformers>=2.2.0" "transformers>=4.30.0" "huggingface-hub>=0.15.0,<1.0"
   ```

3. **Re-encode existing blocks:**
   After installing sentence-transformers, you may need to re-encode blocks:
   ```bash
   # List blocks
   uv run cmemory list-blocks
   
   # Re-encode a specific block (if needed)
   # The system will automatically use real embeddings for new blocks
   ```

4. **Verify embeddings are working:**
   ```bash
   uv run python -c "from sentence_transformers import SentenceTransformer; print('OK')"
   ```

**Note:** The first time you use sentence-transformers, it will download the embedding model (~400MB), which may take a few minutes.

---

### 2. Neo4j Connection Failed

**Symptom:**
```
WARNING - Neo4j connection failed, using fallback
```

**Cause:** Docker Desktop is not running or Neo4j service is not started.

**Solution:**

1. **Start Docker Desktop**

2. **Start Neo4j service:**
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Wait for services to be ready (~15 seconds)**

4. **Verify connection:**
   ```bash
   curl http://localhost:7474
   ```

**Note:** The system will automatically fall back to in-memory graph storage if Neo4j is unavailable. This is fine for basic operations but limits graph features.

---

### 3. ChromaDB Connection Issues

**Symptom:**
```
ChromaDB connection error
```

**Cause:** ChromaDB service not running or port conflict.

**Solution:**

1. **Check if ChromaDB is running:**
   ```bash
   cd docker
   docker-compose ps
   ```

2. **Restart services:**
   ```bash
   docker-compose restart chromadb
   ```

3. **If using local ChromaDB (default):**
   - The system uses an in-process ChromaDB by default
   - No Docker service needed for basic usage
   - Check for port conflicts if you see connection errors

---

### 4. CLI Command Not Found

**Symptom:**
```bash
uv run cmemory --help
# error: Failed to spawn: `cmemory`
```

**Cause:** Package not installed in current environment.

**Solution:**

1. **Install the package:**
   ```bash
   uv pip install -e .
   ```

2. **Or use module syntax:**
   ```bash
   uv run python -m cmemory.cli_entry --help
   ```

---

### 5. Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'cmemory'
```

**Cause:** Python path not set correctly or package not installed.

**Solution:**

1. **Install in development mode:**
   ```bash
   uv pip install -e .
   ```

2. **Check Python path:**
   ```bash
   uv run python -c "import sys; print('\n'.join(sys.path))"
   ```

3. **Verify installation:**
   ```bash
   uv run python -c "import cmemory; print(cmemory.__version__)"
   ```

---

### 6. Dependency Version Conflicts

**Symptom:**
```
ImportError: huggingface-hub>=0.34.0,<1.0 is required but found huggingface-hub==1.1.2
```

**Cause:** Incompatible versions of transformers ecosystem packages.

**Solution:**

1. **Reinstall with compatible versions:**
   ```bash
   uv pip install --upgrade "sentence-transformers>=2.2.0" "transformers>=4.30.0" "huggingface-hub>=0.15.0,<1.0"
   ```

2. **Or use a fresh environment:**
   ```bash
   # Create new venv
   python -m venv .venv-new
   .venv-new\Scripts\activate
   uv pip install -e .
   ```

---

### 7. File Encoding Issues (Windows)

**Symptom:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Cause:** Windows console encoding doesn't support Unicode characters.

**Solution:**

1. **Set console encoding:**
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   ```

2. **Or use ASCII-safe output:**
   - The CLI already uses ASCII-safe output (`[OK]`, `[ERROR]`)
   - If you see Unicode errors, report them as bugs

---

### 8. Empty Search Results After Installing sentence-transformers

**Symptom:**
- Installed sentence-transformers successfully
- Still getting "No results found"
- Warning still says "dummy embeddings"

**Cause:** Existing blocks were encoded with dummy embeddings before sentence-transformers was installed.

**Solution:**

1. **Delete and re-ingest blocks:**
   ```bash
   # Remove old blocks (optional - backup first!)
   rm knowledge/*.md
   
   # Re-ingest your knowledge blocks
   uv run cmemory ingest your-file.md
   ```

2. **Or re-encode existing blocks:**
   - The system will use real embeddings for newly encoded blocks
   - Old blocks with dummy embeddings won't match semantic queries

---

## Getting Help

If you encounter issues not covered here:

1. **Check logs:** Look for WARNING/ERROR messages in the output
2. **Verify installation:** Run `uv pip list` to see installed packages
3. **Test components:** Try importing modules individually
4. **Check documentation:** See `docs/` folder for detailed guides

## Reporting Issues

When reporting issues, include:
- Python version: `python --version`
- OS and version
- Full error message
- Steps to reproduce
- Output of `uv pip list | Select-String -Pattern "cmemory|sentence|transformers"`

