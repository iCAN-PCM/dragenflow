import nox


@nox.session(python=["3.8", "3.9"])
def tests(session):
    """Run tests with pytest"""
    session.install("poetry")
    session.install("poetry", "install")
    tests = ["test/"]
    session.run("pytest", *tests)


@nox.session
def lint(session):
    """lint the files"""
    session.install("black")
    session.install("flake8")
    session.run("black", "--check", ".")
    session.run("flake8", ".")


@nox.session
def typing(session):
    """do python static type checks"""
    session.install("poetry")
    session.run("poetry", "install")
    session.run("mypy", ".")
