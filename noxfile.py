import tempfile

import nox

locations = ["tests", "src"]


@nox.session(python=["3.8"])
def tests(session):
    """Run tests with pytest"""
    session.install("poetry")
    session.run("poetry", "install", external=True)
    tests = ["tests/"]
    session.run("pytest", *tests, external=True)


@nox.session(python=["3.8"])
def lint(session):
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-black",
        "flake8-bugbear",
        "flake8-import-order",
        "flake8-bandit",
    )
    session.run("flake8", *args)


@nox.session(python="3.8")
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")


@nox.session(python=["3.8"])
def typing(session):
    """do python static type checks"""
    args = session.posargs or ["--disable=import-error", *locations]
    session.install("poetry")
    session.run("poetry", "install", external=True)
    session.install("pytype")
    session.run("pytype", *args, external=True)
