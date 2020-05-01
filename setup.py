import sys
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as fp:
    install_requires = fp.read()

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')

setup(
    name='slackify',
    version='0.0.2',
    url='https://github.com/Ambro17/Flask-Slack',
    author='Nahuel Ambrosini',
    author_email='ambro17.1@gmail.com',
    description='Pythonic API for modern slack bots',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['slackify'],
    package_dir={'': 'src'},
    install_requires=install_requires,
    python_requires='>=3.6'
)
