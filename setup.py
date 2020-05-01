import sys
from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.read()

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')

setup(
    name='slackify',
    version='0.0.1',
    url='https://github.com/Ambro17/Flask-Slack',
    author='Nahuel Ambrosini',
    author_email='ambro17.1@gmail.com',
    description='Pythonic API for modern slack bots',
    packages=['slackify'],
    package_dir={'': 'src'},
    install_requires=install_requires,
    python_requires='>=3.6'
)
