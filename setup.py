"""
Setup script for GPT Genius package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gpt-genius",
    version="0.1.0",
    author="GPT Genius Team",
    author_email="contact@gpt-genius.com",
    description="Un framework d'IA pour la génération et l'amélioration de code automatisées",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gpt-genius/gpt-genius",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gpt-genius=gpt_genius.applications.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "gpt_genius": ["preprompts/*"],
    },
)