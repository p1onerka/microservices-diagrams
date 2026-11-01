# Contributing

Contributions are welcome. The project is licensed under the MIT License, and contributions are accepted under the same license.

## Setup

Use Python 3.14, the version CI runs:

```bash
pip install -r requirements.txt
```

Running `generate-diagram.sh` also needs the [CodeQL CLI](https://codeql.github.com/docs/codeql-cli/) on `PATH`. Optional: install the hooks from `.pre-commit-config.yaml` so Black 26.10.1 and Flake8 7.5.0 run before each commit. Those are the same versions as in `requirements.txt`.

## Checks

Before opening a pull request, format, lint and test:

```bash
black .
flake8 .
python -m pytest --cov=. --cov-fail-under=80
```

Flake8 ignores `E501`, `W291` and `W503` (see `.flake8`): line length, trailing whitespace and the line-break style Black produces. Coverage must stay at or above 80%.

Documentation is built from `docs/`:

```bash
cd docs
make html
```

## Pull requests

Branch from `main`. In the description, say what changed and why. Keep the public behavior of the diagram pipeline covered by tests in `tests/`.

CodeQL queries live in `codeql-query/` (Java) and `codeql-query-js/` (JavaScript). The Python side is `data_analyzer.py`, `mermaid_constructor.py` and `diag_drawer.py`. OpenCode agents used by the experiment are in `.opencode/agents/`.

Do not commit CodeQL databases (`codeql-dbs/`), virtual environments or secrets.
