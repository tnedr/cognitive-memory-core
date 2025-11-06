"""Setup script for cognitive-memory-core."""

from setuptools import find_packages, setup

setup(
    name="cognitive-memory-core",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "markdown-it-py>=3.0.0",
        "orjson>=3.9.0",
        "neo4j>=5.15.0",
        "chromadb>=0.4.22",
        "langchain>=0.1.0",
        "langchain-community>=0.0.20",
        "sentence-transformers>=2.2.2",
        "faiss-cpu>=1.7.4",
        "click>=8.1.7",
        "pyyaml>=6.0.1",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "cmemory=src.cli:cli",
        ],
    },
)

