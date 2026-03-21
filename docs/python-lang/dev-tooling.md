# Python: Dev Tooling — Ruff, Pylance, and mypy

Three complementary tools cover the full quality-assurance surface of a Python project: **Ruff** for linting and formatting, **Pylance** for IDE intelligence and basic type checking, and **mypy** for deep static type analysis.

## Ruff

A single tool that replaces flake8, isort, black, and pylint. Written in Rust (by Astral, same team behind `uv`). Handles **linting** and **formatting**.

```bash
uv add --dev ruff            # add as dev dependency
uv run ruff check .          # lint
uv run ruff format .         # format
```

### Config in `pyproject.toml`

```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP"]  # pick rule sets
```

Common rule sets:

| Code | What it checks |
|---|---|
| `E` | pycodestyle errors |
| `F` | pyflakes (unused imports, undefined names) |
| `I` | isort (import ordering) |
| `N` | pep8-naming |
| `UP` | pyupgrade (modernize syntax) |
| `B` | flake8-bugbear (common pitfalls) |
| `SIM` | flake8-simplify |

Full list: https://docs.astral.sh/ruff/rules/

### Pre-commit hook (optional)

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.9.0
  hooks:
    - id: ruff
    - id: ruff-format
```

## Pylance

The VS Code Python extension bundles **Pylance** as its language server. Pylance provides:

- Autocomplete / IntelliSense
- Go to definition / references
- Type checking (via pyright under the hood)
- Refactoring (rename, extract method)
- Hover documentation

Pylance does **not** handle formatting or import sorting — that's Ruff's job.

## Ruff vs Pylance — What Each Owns

| Feature | Pylance | Ruff |
|---|---|---|
| Autocomplete | yes | no |
| Go to definition | yes | no |
| Type checking | yes | no |
| Refactoring | yes | no |
| Style linting | basic | yes (much better) |
| Formatting | no | yes |
| Import sorting | no | yes |

**They are complementary, not competing.** Pylance handles intellisense and type analysis. Ruff handles code style and formatting.

## mypy — Deep Type Checking

Ruff and mypy are also complementary:

- **Ruff** catches style issues, bad patterns, and simple bugs. Works on **syntax**.
- **mypy** catches **type errors** — wrong argument types, None handling, incompatible assignments. Reasons about **data flow**.

Example only mypy catches:

```python
def get_user(id: int) -> User:
    return db.query(User).filter_by(id=id).first()  # returns User | None

user = get_user(1)
print(user.name)  # could be None — mypy catches this, ruff doesn't
```

**Ruff = "is the code well-written?"**
**mypy = "is the code correct?"**

## VS Code Settings

To make Ruff and Pylance work together without conflicts:

```json
// .vscode/settings.json
{
    // Ruff handles formatting and import sorting
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": "explicit"
        }
    },

    // Pylance handles type checking and intellisense
    "python.analysis.typeCheckingMode": "basic"
}
```

Key points:
- Set Ruff as the **default formatter** so it owns formatting and import sorting
- Pylance's built-in linting is minimal and won't conflict with Ruff in practice
- `typeCheckingMode` controls how strict Pylance's type checking is (`off`, `basic`, `standard`, `strict`)

### Extension version vs project version

The Ruff VS Code extension bundles its own ruff binary. To use the project's pinned version instead:

```json
{
    "ruff.path": [".venv/bin/ruff"]
}
```

In practice, minor version differences rarely matter since CI runs the pinned version (`uv run ruff check .`) as the final authority.

## Summary

| Tool | Role | Install |
|---|---|---|
| **Ruff** | Linting + formatting | `uv add --dev ruff` |
| **Pylance** | Intellisense + type checking | VS Code Python extension |
| **mypy** | Deep static type analysis | `uv add --dev mypy` |

All three work together. No conflicts when configured as above.
