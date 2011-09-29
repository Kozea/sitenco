from setuptools import setup, find_packages

setup(
    name="SiteNCo",
    packages=find_packages(),
    install_requires=["Dyko >= 0.3", "CSStyle", "Flask", "docutils", "pyyaml",
                      "lxml"])
