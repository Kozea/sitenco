from setuptools import setup, find_packages

setup(
    name="SiteNCo",
    packages=find_packages(),
    install_requires=["CSStyle", "Flask", "docutils", "pyyaml",
                      "lxml", "Pygments", "pygal"])
