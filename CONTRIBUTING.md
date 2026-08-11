# How to contribute

## Using the issue tracker

You can suggest features, enhancements, or report bugs on our [issue tracker](https://github.com/k-tech-italy/ktcalendars/issues).

You can also use the issue tracker to find an open issue for you to work on. Please mention in the issue that you are working on it.

## Changing the codebase

You should fork this project, make changes in your own fork, then submit a pull request against the `develop` branch.

Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) convention (enforced with [commitizen](https://commitizen-tools.github.io/commitizen/), see `.cz.toml`); flag breaking changes with `!` and a `BREAKING CHANGE:` footer.

To start working on this project:
* Install [uv](https://docs.astral.sh/uv)
* Clone the repository:
    ```bash
    # using HTTPS
    git clone https://github.com/k-tech-italy/ktcalendars.git

    # using SSH
    git clone git@github.com:k-tech-italy/ktcalendars.git
    ```
* If you use [direnv](https://direnv.net/), copy the `.envrc.example` file as follows, otherwise skip this step:
    ```bash
    cp .envrc.example .envrc
    ```
* Create a virtual environment for the project using uv. Make sure you use the earliest supported Python version:
    ```bash
    uv venv --python 3.10

    # if you're not using direnv, you need to manually activate the virtual environment
    source .venv/bin/activate
    ```
* Install the project's dependencies:
    ```bash
    uv sync
    ```

You **must** make sure that your changes are covered by unit and integration tests, and that it follows the project's stylistic guidelines. In the absence of the latter, you should mimic the style and patterns in the existing codebase.

### Running tests

You should ensure that all tests are passing. We use `pytest` to write and run tests.
```bash
pytest tests
```

You should also make sure that your changes work with all supported versions of Python. For that, we are using `tox`:
```bash
tox
```

### Formatting and linting

This project uses `ruff` to format and lint code.

Run the lints using `tox`:
```bash
tox -e lint
```

Format the code using `ruff`:
```bash
ruff check --fix
ruff format
```

## Release process

Releases are cut from `master` and are fully driven by git tags; maintainers
release as follows:

1. Make sure `develop` is green (the *Lint* and *Test* workflows run on every
   push) and that `CHANGELOG.md` describes the changes being released: rename
   the `Unreleased` section to the new version and date.
2. Merge `develop` into `master`. Pushing to `master` automatically rebuilds
   and deploys the documentation to GitHub Pages (*Documentation* workflow).
3. Tag the merge commit on `master` with the bare [PEP 440](https://peps.python.org/pep-0440/)
   version (no `v` prefix, e.g. `1.1.0`) and push the tag:
    ```bash
    git tag 1.1.0
    git push origin 1.1.0
    ```
   There is no version committed to the repository: the package version is
   derived from the git tag at build time by [hatch-vcs](https://github.com/ofek/hatch-vcs),
   which generates `src/ktcalendars/version.py`.

   Alternatively, run `uvx --from commitizen cz bump` on `master`: it derives
   the increment from the conventional commits since the last tag, updates
   `CHANGELOG.md` and creates the tag for you (run it before pushing, then
   push `master` and the tag). Note that it must be run on `master` — the
   release tags are not reachable from `develop`, so commitizen cannot see
   the current version there.
4. The tag push triggers the *Publish* workflow, which builds the sdist and
   wheel with `uv build` and publishes them:
    * tags containing `-rc`, `-beta` or `-alpha` (e.g. `1.1.0-rc1`) go to
      [TestPyPI](https://test.pypi.org/p/ktcalendars);
    * all other tags go to [PyPI](https://pypi.org/p/ktcalendars).
