from setuptools import setup
from SGLauncher import __version__ as VERSION

install_requires = [
    'PySimpleGUI',
]

packages = [
    'SGLauncher',
]

setup(
    name='SGLauncher',
    version=VERSION,
    packages=packages,
    install_requires=install_requires,
)
