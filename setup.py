from setuptools import setup
import re

def read(filename):
    with open(filename) as f:
        return f.read()

__version__ = re.search(r'^__version__ = ([\'"])(?P<version>.*)\1$',
                        read('numtraits.py'), re.M).groupdict()['version']

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = read('README.md')

setup(
    version=__version__,
    url="https://github.com/astrofrog/numtraits",
    name="numtraits",
    description='Numerical traits for Python objects',
    long_description=long_description,
    py_modules=['numtraits'],
    license='BSD',
    author='Thomas Robitaille',
    author_email='thomas.robitaille@gmail.com',
    install_requires=['numpy','traitlets']
)
