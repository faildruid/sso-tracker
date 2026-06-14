# ⚔ Shattered Sun Offensive - Reputation Tracker

A minimal CLI tool to track your **Shattered Sun Offensive** reputation grind in World of Warcraft (The Burning Crusade).

Just type what WoW shows you — no mental math required.

---

## Reputation brackets (as shown in-game)

| Rank     | Points in bracket | Cumulative |
| -------- | :---------------: | :--------: |
| Neutral  | 0 – 3,000         | 0          |
| Friendly | 0 – 6,000         | 3,000      |
| Honored  | 0 – 6,000         | 9,000      |
| Revered  | 0 – 9,000         | 15,000     |
| Exalted  | 0 – 1,000         | 21,000     |

**Total to Exalted: 22,000 cumulative reputation.**

---

## Requirements

| Tool | Version |
| ------ | --------- |
| Python | ≥ 3.11 |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.4 |

---

## Installation

```bash
# 1. Unzip and enter the project
cd sso_tracker

# 2. Create virtual environment and install dev dependencies
uv sync

# 3. Install the CLI in editable mode
uv pip install -e .
```

The `sso` command is now available:

```bash
uv run sso --help
# or activate the venv:
source .venv/bin/activate
sso --help
```

---

## Usage

### Set your starting reputation

Run this once, entering exactly what WoW shows you:

```text
WoW shows:  Neutral  1089 / 3000
```

```bash
sso init neutral 1089
```

```text
WoW shows:  Revered  4500 / 9000
```

```bash
sso init revered 4500
```

Valid rank names: `neutral`, `friendly`, `honored`, `revered`, `exalted`

---

### Record progress after a run

After each run, just read WoW's reputation panel and type what it shows:

```text
WoW shows:  Neutral  1400 / 3000   (was 1089)
```

```bash
sso add neutral 1400
```

The app calculates the delta automatically (+311 in this example).

Crossing a bracket boundary works too:

```text
WoW shows:  Friendly  100 / 6000   (was Neutral 2900)
```

```bash
sso add friendly 100
```

---

### Show current progress

```bash
sso status
# or just:
sso
```

Example output:

```text
⚔  Shattered Sun Offensive — Rep Tracker
────────────────────────────────────────────────
  Current standing     Neutral (1,400 / 3,000)
  Cumulative total          1,400 / 22,000
  Remaining                20,600

  Run count                     1
  Avg rep / run             311.0
  Est. runs left             66.2

  [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 6.4%
```

---

### Reset all progress

```bash
sso reset
```

### Override save file location

```bash
sso --save-file /tmp/alt_grind.json status
```

Default location: `~/.sso_tracker/progress.json`

---

## Development

### Run tests

```bash
uv run pytest
```

### Run with coverage

```bash
uv run pytest --cov
```

### Lint & format

```bash
uv run ruff check .
uv run ruff format --check .

# Auto-fix
uv run ruff check --fix .
uv run ruff format .
```

---

## Project layout

```text
sso_tracker/
├── src/sso_tracker/
│   ├── __init__.py       # version
│   ├── reputation.py     # rank table + WoW display → cumulative conversion
│   ├── domain.py         # Progress & Run dataclasses, computed stats
│   ├── repository.py     # JSON persistence
│   ├── display.py        # terminal output
│   └── cli.py            # argparse CLI entry point
├── tests/
│   ├── test_reputation.py
│   ├── test_domain.py
│   ├── test_repository.py
│   └── test_cli.py
├── pyproject.toml
├── uv.lock
└── README.md
```
