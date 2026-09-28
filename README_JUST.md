# Justfile Readme

[**Just**](https://github.com/casey/just) _is a handy way to save and run project-specific commands_

`just` (no arguments) lists all recipes.

`just dev-check` run pre-commit auto-fixes and formatters on all files.

`just dev-format` run the ruff formatter (mutates files; review your git diffs after).

`just dev-lint` run the ruff linter (read-only; files are not mutated).

`just dev-typecheck` run the ty type checker.

`just test` run the test suite.

`just venv-install` create the uv Python environment, install all Python dependencies, and install the pre-commit hooks.

`just venv-uninstall` delete the uv Python environment.



# Prerequisites & dependencies

### Install `uv`

uv's documentation is available at [docs.astral.sh/uv](https://docs.astral.sh/uv/).

Install `uv` on macOS and Linux with standalone installers:<br>
`curl -LsSf https://astral.sh/uv/install.sh | sh`

On `uv` Windows with standalone installer:<br>
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`


---
### Install `just`

just's documentation is available at [https://github.com/casey/just#packages](https://github.com/casey/just#packages)

Install `just` on macOS:<br>
`brew install just`

Install `just` on Ubuntu/Debian:<br>
`apt install just`


---
### Install `ruff`

ruff's documentation is available at [docs.astral.sh/ruff](https://docs.astral.sh/ruff/installation/).

The `just` recipes get the pinned ruff version from pyproject.toml. You do not have to install ruff. To run it outside `just`, install the same version.

Install `ruff` on macOS and Linux with standalone installers:<br>
`curl -LsSf https://astral.sh/ruff/0.16.3/install.sh | sh`

On `ruff` Windows with standalone installer:<br>
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/ruff/0.16.3/install.ps1 | iex"`


---
### Install `ty`

ty's documentation is available at [docs.astral.sh/ty](https://docs.astral.sh/ty/installation/).

`just venv-install` installs the pinned ty version from pyproject.toml into `.venv`. You do not have to install ty. To run it outside `just`, install the same version.

Install `ty` on macOS and Linux with standalone installers:<br>
`curl -LsSf https://astral.sh/ty/0.0.72/install.sh | sh`

On `ty` Windows with standalone installer:<br>
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/ty/0.0.72/install.ps1 | iex"`
