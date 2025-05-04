from setuptools import setup, find_packages

setup(
    name="asset_allocation",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas",
        "yfinance",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "asset-allocation=asset_allocation.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Matthew Dudys",
    author_email="mattdudys@gmail.com",
    description="A tool for managing investment portfolio asset allocation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mattdudys/asset-allocation",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
