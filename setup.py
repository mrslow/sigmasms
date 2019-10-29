from setuptools import setup

with open('README.md') as f:
    readme = f.read()

dependencies = ['aiohttp']

setup(
    name='aiosigmasms',
    version='0.2',
    description='Tool for easy working with SigmaSMS API',
    long_description=readme,
    author='Anton Shchetikhin',
    author_email='animal2k@gmail.com',
    py_modules=['aiosigmasms'],
    url='https://github.com/mrslow/aiosigmasms',
    keywords=['api', 'sms', 'sigmasms', 'asyncio', 'aiohttp']
)
