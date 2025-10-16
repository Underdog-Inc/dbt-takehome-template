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
- [`seeds/`](./seeds): Small CSVs you’ll load with `dbt seed`
  - [`seeds/DATA_SUMMARY.md`](./seeds/DATA_SUMMARY.md): Descriptions and key information to be aware of about the data.
- [`models/`](./models): Start in `staging/` then build to `marts/`
- [`macros/`](./macros): Add at least one macro (Jinja)
- [`profiles/`](./profiles): A working DuckDB profile (no external creds)
- [`pyproject.toml`](./pyproject.toml): Project dependencies (managed by **uv**)
- [`scripts/setup.sh`](./scripts/setup.sh) and [`scripts/setup.ps1`](./scripts/setup.ps1): One‑command setup with **uv**

---

## ⚙️ Quick Start (macOS/Linux)

```bash
# 1) Run the setup script (installs uv, creates .venv, installs deps)
bash scripts/setup.sh

# 2) Activate the virtual environment
source .venv/bin/activate

# 3) Set the profiles directory (so dbt finds profiles/profiles.yml)
export DBT_PROFILES_DIR="$PWD/profiles"

# 4) Verify dbt & seed the data
dbt --version
dbt deps
dbt seed --show

# 5) Build (models + tests + docs)
dbt build

# 6) Explore docs locally (from the ./target site)
python -m http.server 8000 -d target && open http://localhost:8000/index.html
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
uv run dbt seed --show
uv run dbt build
```
> If uv run is used, you don't need to manually activate .venv. Both approaches work.

> **Pro tip:** You can also `source .envrc` to set `DBT_PROFILES_DIR` automatically, or use [direnv](https://direnv.net/) for automatic environment loading.

---

## 🧪 Common dbt Commands
```
dbt deps
dbt seed
dbt run
dbt test
dbt build          # run + test + docs
dbt docs generate  # regenerate docs site
```

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
* **Fresh build**: Try `dbt clean && dbt deps && dbt seed && dbt build --full-refresh`.
* **DuckDB file**: The database file lives at `./.dbt/dbt_duckdb.duckdb`.

## Submission
Open an Issue titled `Submission: <Your Name>` with:
* Link to your private repo (grant access to reviewers listed in the prompt)
* Approx. time spent & assumptions
* Anything you’d do with more time