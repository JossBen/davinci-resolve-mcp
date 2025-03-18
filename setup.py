from setuptools import setup, find_packages

setup(
    name="resolve-mcp",
    version="0.1.0",
    description="Model Context Protocol (MCP) server for DaVinci Resolve",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp>=0.3.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "resolve-mcp=resolve_mcp.server:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
