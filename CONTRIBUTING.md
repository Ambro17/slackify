# Contributing to Slackify

First of all, thanks for taking the time to contribute!

The following is a set of guidelines for contributing to `Slackify` on GitHub.
These are mostly guidelines, not rules. Use your best judgment, and feel free
to propose changes to this document in a pull request.


## Contributing to code

Before you start you will need to install docker to get a reproducible environment to run tests.
Refer to [Docker Docs](https://docs.docker.com/get-docker/) for instructions on how to do so.

You will first need to clone the repository using `git` and place yourself in its directory:

```bash
git clone git@github.com:Ambro17/slackify.git
cd slackify
```

Now, use docker to install all the required dependencies and ensure a working
environment

```bash
docker build . -t slackify
docker run -it --rm -v $PWD:/app
```

Once inside the docker container you can run your tests with
```python
pytest
```
Slackify uses flake8 to maintain certain coding style conventions so it's a good idea to also run
```python
flake8
```
before opening a pull request to ensure your style matches `pep8` conventions
