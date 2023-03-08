import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="okcoinv5", # Replace with your own username
    version="0.0.1",
    author="EP-FTW",
    author_email="info@milightningrod.com",
    description="A Python package for interfacing with okcoin API V5, which includes Lightning functionality.",
    long_description="Longer description here.",
    long_description_content_type="text/markdown",
    url="https://github.com/REAL-ERP/python-api-for-okcoin-V5/",
    project_urls={
        "Bug Tracker": "https://github.com/REAL-ERP/python-api-for-okcoin-V5/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.10",
)
