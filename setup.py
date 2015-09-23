from setuptools import setup

from numtraits import __version__

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md') as infile:
        long_description = infile.read()

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
