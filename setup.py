from setuptools import setup, find_packages

setup(
    name="shrike-cli",
    version="1.0.0a0",
    description="Deterministic Financial Risk Scanner for Stripe Integrations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="NANIEXISTS",
    author_email="support@shrike.pro",
    url="https://cli.shrike.pro",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "rich",
        "google-genai",
        "pydantic-settings"
    ],
    entry_points={
        "console_scripts": [
            "shrike=shrike_cli.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Security",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
