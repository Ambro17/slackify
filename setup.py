import sys
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')

setup(
    name='slackify',
    version='0.1.1',
    url='https://github.com/Ambro17/Flask-Slack',
    author='Nahuel Ambrosini',
    author_email='ambro17.1@gmail.com',
    description='Pythonic API for modern slack bots',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['slackify'],
    package_dir={'': 'src'},
    install_requires=[
        "Flask>=1.0.0",
        "slackclient>=2.5.0",
        "requests>=2.0.0",
        "pyee>=7.0.0",
    ],
    python_requires='>=3.6'
)
