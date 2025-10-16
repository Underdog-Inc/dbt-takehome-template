# TASK — Analytics Engineer dbt Take‑Home

## Scenario
You’re joining the analytics team for a consumer product with user accounts and transactions. You will model core facts and dimensions from the provided raw CSVs, then surface a metric and a small semantic layer for analysis.

## Data
You have two CSV seeds (`seeds/`):
- **customers.csv** — one row per user (id, created_at, country, marketing_channel, …)
- **orders.csv** — one row per order (order_id, customer_id, order_ts, amount, status)

Assume orders in `status IN ('completed', 'refunded')` and amounts are in USD.

> Data volume is intentionally small; optimize for clarity and correctness rather than performance.

## Requirements
1. **Modeling**
   - Create **staging** models that clean and type‑cast the seeds.
   - Build a **marts** model at the monthly grain that reports revenue and order counts per customer.
   - Implement an **incremental** strategy for the marts model (idempotent). Document your choice of unique key and strategy.
2. **Testing**
   - Add **column tests** (e.g., `unique`, `not_null`) for key fields.
   - Add **a relationship test** between marts and staging on `customer_id`.
3. **Documentation**
   - Add descriptions in `schema.yml` and a short `README.md` in `models/staging/` explaining your staging conventions.
4. **Macro**
   - Implement at least **one reusable macro** (e.g., a `safe_cast` helper or a date boundary macro) and use it.
5. **Analytics Output**
   - In `marts/`, include a model that yields: `month, customer_id, order_count, revenue` (completed orders only).
   - Add a second view/model that surfaces **Top 10 countries by revenue** with tie‑breakers (document your rule).
6. **Docs**
   - Ensure `dbt build` generates a docs site. We’ll review lineage.

## Deliverables
- Models in `models/staging/` and `models/marts/`
- Tests in `models/tests/` or in model YAML
- Macro(s) in `macros/`
- Documentation (model/column descriptions)
- Incremental config on the monthly marts model
- All CI checks (if configured) passing

## Timebox
Aim for **2–3 hours**. If you decide not to implement something, explain the trade‑off in your repo README.

## Submission
Open an Issue titled `Submission: <Your Name>` and include:
- Repo URL (grant access to reviewers: `@eamon-glackin` and team)
- Approx. time spent
- Assumptions & edge cases
- If anything differs from local DuckDB defaults

## Rubric (what we look for)
- **Modeling & structure (20%)** — staging vs marts separation, naming, clarity
- **Testing (15%)** — appropriate tests and coverage
- **Documentation (10%)** — useful descriptions and READMEs
- **Incremental strategy (10%)** — correctness, idempotence, grain
- **SQL quality (5%)** — readability, maintainability, macro use
- **Execution (25%)** — commit hygiene, reproducible build, docs
- **Polish / Bonus (15%)** — thoughtful macros, snapshots/rationale, semantic layering

> It’s okay to leave notes on “what I’d do next in production.”
