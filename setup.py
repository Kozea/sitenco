from setuptools import find_packages, setup

tests_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-flake8',
    'pytest-isort',
]

setup(
    name="Sitenco",
    version="0.1.dev0",
    description="Simple websites for simple projects.",
    url="https://kozea.fr",
    author="Kozea",
    packages=find_packages(),
    include_package_data=True,
    scripts=['launcher.py'],
    install_requires=[
        'docutils-html5-writer',
        'Flask',
        'PyYAML',
        'pygments',
    ],
    tests_requires=tests_requirements,
    extras_require={'test': tests_requirements}
)
