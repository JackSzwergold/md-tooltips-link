from setuptools import setup
import os

def readfile(filename):
    with open(filename, **{"encoding": "utf-8"}) as fp:
        filecontents = fp.read()
    return filecontents

setup(
    maintainer="Matt Pitkin",
    maintainer_email="matthew.pitkin@ligo.org",
    name="md-tooltips-link",
    version="0.2.4",
    description="A Python markdown extension for implementing a glossary with tooltips",
    py_modules=["mdtooltipslink"],
    install_requires = \
          readfile(os.path.join(os.path.dirname(__file__), "requirements.txt")),
    include_package_data=True,
    url="https://github.com/mattpitkin/md-tooltips-link",
)
