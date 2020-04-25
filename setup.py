from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='Flask-Slack',
    version='0.0.1',
    url='https://github.com/Ambro17/Flask-Slack',
    author='Nahuel Ambrosini',
    author_email='ambro17.1@gmail.com',
    description='Flask powered slack bots',
    packages=['flask_slack'],
    package_dir={'': 'src'},
    install_requires=install_requires,
)
