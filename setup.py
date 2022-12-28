import os
import codecs
from pathlib import Path

from setuptools import setup, find_packages

MODULE_NAME = "wallapop_scraper"

###############################################################################


def read_rel(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as f:
        return f.read()


def get_version(rel_path):
    for line in read_rel(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]

    raise RuntimeError("Unable to find version string.")


###############################################################################

AUTHORS = ["Daniel Verdu", "Raul Sanz"]
DESCRIPTION_SHORT = "A Python package for scraping data from Wallapop website"
VERSION = get_version(os.path.join(MODULE_NAME, "__init__.py"))

# Long description
with open("README.md", encoding="utf-8") as f:
    DESCRIPTION_LONG = f.read()

# Requirements
with open("requirements.txt", encoding="utf-8") as f:
    requirements = [
        x for x in map(str.strip, f.read().splitlines()) if x and not x.startswith("#")
    ]

# Additional (keyword) arguments
kwargs = {"entry_points": {"console_scripts": []}}

###############################################################################

setup(
    name=MODULE_NAME,
    version=VERSION,
    author=AUTHORS,
    author_email="",
    description=DESCRIPTION_SHORT,
    long_description=DESCRIPTION_LONG,
    license="",
    url="",
    install_requires=[requirements],
    packages=find_packages(),
    package_data={},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    **kwargs,
)
