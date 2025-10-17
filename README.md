# dbt Take‑Home Assessment

Welcome! This repository contains a self‑contained dbt project scaffold and a small dataset for a practical analytics engineering exercise. You'll model data, add tests, document your work, and run everything locally using **DuckDB**—no cloud creds required.

> **Timebox:** We expect ~2–3 hours. Focus on clarity of thinking, data modeling choices, and test coverage—not boilerplate.

---

## 🚀 Getting Started: Create Your Private Repository

**Before you begin working on the assessment, please create your own private repository from this template:**

1. **Click the "Use this template" button** at the top of this repository page (or visit the [template repo](https://github.com/Underdog-Inc/dbt-takehome-template))
2. Select **"Create a new repository"**
3. Choose a repository name (e.g., `dbt-takehome-yourname`)
4. **Set visibility to Private** ⚠️
5. Click **"Create repository"**
6. Clone your new private repository to your local machine:
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   cd YOUR-REPO-NAME
   ```
7. **Grant access to reviewers** as specified in [`TASK.md`](./TASK.md)

Now you're ready to start the assessment! 🎉

---

## 🧭 Contents
- [`TASK.md`](./TASK.md): The full prompt, deliverables, and rubric
- [`source_data/`](./source_data): **Parquet source data files** (efficient storage, fast queries)
  - [`source_data/DATA_SUMMARY.md`](./source_data/DATA_SUMMARY.md): Comprehensive data documentation and schema details
- [`models/`](./models): Start in `staging/` then build to `marts/`
- [`macros/`](./macros): Add at least one macro (Jinja)
- [`profiles/`](./profiles): A working DuckDB profile (no external creds)
- [`pyproject.toml`](./pyproject.toml): Project dependencies (managed by **uv**)
- [`scripts/setup.sh`](./scripts/setup.sh) and [`scripts/setup.ps1`](./scripts/setup.ps1): One‑command setup with **uv**
- [`DUCKDB_QUERIES.md`](./DUCKDB_QUERIES.md): Example queries and source configuration guide

---

## ⚙️ Quick Start (macOS/Linux)

```bash
# 1) Run the setup script (installs uv, creates .venv, installs deps)
bash scripts/setup.sh

# 2) Activate the virtual environment
source .venv/bin/activate

# 3) Set the profiles directory (so dbt finds profiles/profiles.yml)
export DBT_PROFILES_DIR="$PWD/profiles"

# 4) Verify dbt and install dependencies
dbt --version
dbt deps

# 5) Build (models + tests + docs)
dbt build

# 6) Explore docs locally (from the ./target site)
dbt docs generate && dbt docs serve
```

## ⚙️ Quick Start (Windows PowerShell)
```
# 1) Run the setup script (installs uv, creates .venv, installs deps)
./scripts/setup.ps1

# 2) Activate the virtual environment
. .\.venv\Scripts\Activate.ps1

# 3) Set the profiles directory
$env:DBT_PROFILES_DIR = "$PWD\profiles"

# 4) Verify & run
uv pip list
uv run dbt --version
uv run dbt deps
uv run dbt build
```
> If uv run is used, you don't need to manually activate .venv. Both approaches work.

> **Pro tip:** You can also `source .envrc` to set `DBT_PROFILES_DIR` automatically, or use [direnv](https://direnv.net/) for automatic environment loading.

---

## 🧪 Common dbt Commands
```
dbt deps
dbt run
dbt test
dbt build          # run + test + docs
dbt docs generate  # regenerate docs site
```

---

## 🦆 Querying Data with DuckDB

You have multiple ways to explore the Parquet source data:

### Option 1: Through dbt
```bash
# Set up sources (see DUCKDB_QUERIES.md for examples)
# Create models/staging/_sources.yml

# Query via dbt models
dbt run

# View results in generated docs
dbt docs generate
```

### Option 2: Direct Parquet Queries with DuckDB CLI
Query Parquet files directly using DuckDB (requires separate installation):

**Install DuckDB CLI:**
```bash
# macOS
brew install duckdb

# Or download from https://duckdb.org/docs/installation/
```

**Query examples:**
```bash
# Single query
duckdb -c "SELECT * FROM 'source_data/users.parquet' LIMIT 10"

# Join multiple Parquet files
duckdb -c "SELECT u.user_id, u.state, COUNT(e.entry_id) as total_entries
  FROM 'source_data/users.parquet' u
  LEFT JOIN 'source_data/entries.parquet' e ON u.user_id = e.user_id
  GROUP BY u.user_id, u.state
  LIMIT 10"
```

### Option 3: Interactive DuckDB CLI
```bash
# Query Parquet files interactively
duckdb

# Or query your dbt database (after running dbt run)
duckdb ./.dbt/dbt_duckdb.duckdb
```

**📖 For more query examples, see [`DUCKDB_QUERIES.md`](./DUCKDB_QUERIES.md)**

---

## 🗂️ Suggested Project Structure
```
.
├─ README.md
├─ TASK.md
├─ pyproject.toml
├─ dbt_project.yml
├─ packages.yml
├─ macros/
├─ models/
│  ├─ staging/
│  ├─ marts/
│  └─ tests/
├─ seeds/
├─ profiles/
│  └─ profiles.example.yml
└─ scripts/
   ├─ setup.sh
   └─ setup.ps1
```

---

## 🔧 Troubleshooting
* **Python version**: Use Python 3.11–3.12. If multiple Pythons installed, point `uv` at the desired one: `uv python pin 3.11` (optional).
* **Profiles error** (`Could not find profile named 'dbt-takehome'`): dbt normally looks for `~/.dbt/profiles.yml`. This repo uses a local `profiles/profiles.yml`. Set the environment variable:
  ```bash
  export DBT_PROFILES_DIR="$PWD/profiles"
  ```
  You'll need to run this in each new terminal session, or add it to your shell profile.
* **Fresh build**: Try `dbt clean && dbt deps && dbt build --full-refresh`.
* **DuckDB file**: The database file lives at `./.dbt/dbt_duckdb.duckdb`.
* **Source data**: The Parquet files are in `source_data/`. See [`DUCKDB_QUERIES.md`](./DUCKDB_QUERIES.md) for examples of setting up sources.

## Submission
Open an Issue on the [template repo](https://github.com/Underdog-Inc/dbt-takehome-template) titled `Submission: <Your Name>` with:
* Link to your private repo (grant access to reviewers listed in the prompt)
* Approx. time spent & assumptions
* Anything you’d do with more time