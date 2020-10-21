from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


version = "0.1.5"


setup(
    name="askstack",
    version=version,
    description="Search answers on stackoverflow",
    long_description=long_description,
    author="Pedro Buteri Gonring",
    author_email="pedro@bigode.net",
    url="https://github.com/pdrb/askstack",
    license="MIT",
    classifiers=[],
    keywords="search answer ask stack overflow command line",
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=["requests", "lxml"],
    tests_require=["pytest", "responses"],
    entry_points={"console_scripts": ["askstack=askstack.askstack:cli"],},
)
