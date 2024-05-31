from setuptools import setup

setup(
    name='lemlist',
    version='v0.0.3',
    description='Lemlist API client for Python.',
    author='Mehmet Oner Yalcin',
    author_email='oneryalcin@gmail.com',
    url="https://github.com/oneryalcin/lemlist",
    packages=['lemlist'],
    install_requires=['requests>=2.28.0', "tenacity>=8.2.3"],
)
