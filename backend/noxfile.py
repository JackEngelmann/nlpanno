import nox


@nox.session
def tests(session):
    session.install(".[tests,develop]")
    session.run("pytest")


@nox.session
def isort(session):
    session.install(".[tests,develop]")
    session.run("isort", ".")


@nox.session()
def black(session):
    session.install(".[tests,develop]")
    session.run("black", ".")


@nox.session
def flake8(session):
    session.install(".[tests,develop]")
    session.run("flake8", ".", "--max-line-length", "88")


@nox.session
def mypy(session):
    session.install(".[tests,develop]")
    session.run("mypy", "src/", "tests/")


@nox.session
def pylint(session):
    session.install(".[tests,develop]")
    session.run("pylint", "src/", "tests/")
