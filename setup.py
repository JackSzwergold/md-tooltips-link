from setuptools import setup

setup(
    maintainer="Matt Pitkin",
    maintainer_email="matthew.pitkin@ligo.org",
    name="md-tooltips-link",
    version="0.1",
    description="A Python markdown extension for implementing a glossary with tooltips",
    py_modules=["mdtooltipslink"],
    install_requires = ["markdown>=2.5"],
    url="https://github.com/mattpitkin/md-tooltips-link",
)
