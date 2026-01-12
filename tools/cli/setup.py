from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scs-tools",
    version="0.1.0",
    author="SCS Contributors",
    author_email="",
    description="CLI tools for Structured Context Specification (SCS) project scaffolding",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tim-mccrimmon/structured-context-spec",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        "validator": ["scs-validator>=0.1.0"],
    },
    entry_points={
        "console_scripts": [
            "scs=scs_tools.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "scs_tools": [
            "templates/**/*.yaml",
            "templates/**/*.yml",
            "templates/**/*.md",
            "templates/**/*.txt",
        ],
    },
)
