from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='fcs',
    description='Focused Crawling Services',
    long_description=long_description,
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/agh-glk/fcs',
    author='AGH-GLK',
)
