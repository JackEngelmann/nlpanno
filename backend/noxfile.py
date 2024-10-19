import nox


@nox.session
def ruff_check(session: nox.Session) -> None:
	session.install(".[tests,develop]")
	session.run("ruff", "check", "src/", "tests/")


@nox.session
def ruff_format(session: nox.Session) -> None:
	session.install(".[tests,develop]")
	session.run("ruff", "format", "src/", "tests/", "--check")


@nox.session
def tests(session: nox.Session) -> None:
	session.install(".[tests,develop]")
	session.run("pytest")


@nox.session
def mypy(session: nox.Session) -> None:
	session.install(".[tests,develop]")
	session.run("mypy", "src/", "tests/")
