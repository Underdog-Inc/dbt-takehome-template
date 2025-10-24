# TASK — Analytics Engineer dbt Take‑Home

## Scenario
You're joining the analytics engineering team at Underdog Fantasy, a daily fantasy sports platform. You will model core business entities from the provided raw Parquet sources — users, contests, entries, and financial transactions — then surface key metrics and insights for analysis.

## Data
You have five Parquet source files (`source_data/`):
- **users.parquet** — one row per user (user_id [UUID], created_at, state, signup_channel, kyc_status)
- **contests.parquet** — one row per fantasy contest (contest_id [UUID], contest_type, entry_fee, start_time, status, max_entries, prize_pool)
- **entries.parquet** — one row per user entry into a contest (entry_id [UUID], user_id, contest_id, entry_time, entry_fee, payout_amount, bonus_funds_used, cash_used, status)
- **deposits.parquet** — one row per user deposit (deposit_id [UUID], user_id, deposit_ts, amount, payment_method, status, is_admin_deposit)
- **withdrawals.parquet** — one row per user withdrawal (withdrawal_id [UUID], user_id, withdrawal_ts, amount, status)

**Setting up sources:** You'll need to configure these Parquet files as dbt sources. See [`DUCKDB_QUERIES.md`](./DUCKDB_QUERIES.md) for an example source configuration.

Assume:
- **All IDs are UUIDs** (e.g., `f4a06ec5-a762-459b-9413-8fc28b08d505`) for realistic production-like data
- **KYC Requirements**: Only users with `kyc_status = 'verified'` can make deposits, withdrawals, or enter contests. Only verified users have state information.
- Contests in `status IN ('completed', 'cancelled')` are final
- Entries are linked to completed contests for payout calculations
- Financial transactions in `status = 'completed'` are settled
- All amounts are in USD
- **Bonus funds**: Admin deposits (`is_admin_deposit = TRUE`) credit promotional funds to users. When entering contests, bonus funds are consumed first before user cash. **Only cash entry fees (`cash_used`) count toward net gaming revenue**, not total `entry_fee`.
- **Data quality**: Some records may have NULLs or missing values that need cleaning in staging.
- **Dataset size**: 40,000 users, 4,000 contests, 600,000 entries, 64,000 deposits, 16,000 withdrawals

> Data volume includes thousands of records to simulate realistic scenarios. See `source_data/DATA_SUMMARY.md` for detailed information.

## Key Business Concepts

### Bonus Funds vs Cash Revenue
This is a critical distinction in fantasy sports platforms:
- Admin deposits are **promotional bonuses** that don't represent real user deposits
- Users spend bonus funds before their cash when entering contests
- **Net gaming revenue = cash entry fees - payouts** (excludes bonus funds)
- Bonus deposits should NOT be counted as user cash deposits

### Entry Economics
- Total `entry_fee` = `bonus_funds_used` + `cash_used`
- Winners receive `payout_amount` based on contest performance
- Cancelled contests refund the full `entry_fee` as `payout_amount`

### Data Quality
The dataset intentionally includes ~1-2% records with missing/NULL values to test your staging layer handling.

## Requirements
1. **Modeling**
   - Set up **dbt sources** for the Parquet files (create `models/staging/_sources.yml`). Reference them using `{{ source('source_name', 'table_name') }}` in your models.
   - Create **staging** models that clean and type‑cast the sources. Handle NULLs, missing values, and data quality issues. See `models/staging/stg_entries_example.sql` for a reference pattern.
   - Build a **user-level marts model** at a daily grain with key metrics per user:
     - Total cash entry fees paid (`cash_used`)
     - Total bonus entry fees used (`bonus_funds_used`)
     - Total payouts won
     - Net gaming revenue (cash entry fees - payouts)
     - User cash deposits (excluding admin/bonus deposits)
     - Withdrawals
     - Net balance change
   - **Choose 2-3 additional mart models** from these suggestions or propose your own:
     - `fct_contests` — Contest-level metrics: fill rate (entries/max_entries), total revenue, margin, payout efficiency
     - `fct_deposits_overview` — Deposit success rates by payment method, average amounts, admin vs user deposits
     - `fct_withdrawals_overview` — Withdrawal completion rates, failure analysis
     - **Top 10 states by net gaming revenue** with tie‑breakers (document your rule).
   - Create an incremental (idempotent) model that tracks the following metrics for each day of a user's lifetime
     - Metrics
       - Total cash entry fees paid in the last 7 days
       - Total cash entry fees paid life to date
       - Total bonus entry fees used in the last 7 days
       - Total bonus entry fees used life to date
       - Net gaming revenue in the last 7 days
       - Net gaming revenue life to date
     - You can use the first user - daily model you created, if helpful
     - Explain your choice of unique key, time grain, and incremental strategy.
   - **Bonus:** Build a weekly grain model with weeks starting on Tuesday to align with the NFL calendar. Consider creating a macro for this date logic.
2. **Testing**
   - Add **column tests** (e.g., `unique`, `not_null`) for key fields.
   - Add **relationship tests** between marts and staging (e.g., `user_id` relationships).
   - Add a **custom test** to validate business logic (e.g., bonus_funds_used ≤ entry_fee, total payouts ≤ prize pool).
   - Add tests to catch data quality issues (e.g., accepted values for status fields).
3. **Documentation**
   - Add descriptions in `schema.yml` and a short `README.md` in `models/staging/` explaining your staging conventions.
4. **Macro**
   - Implement at least **one reusable macro** and use it in your models. Examples: safe type casting, date calculations, or custom business logic.
5. **Docs**
   - Ensure `dbt build` generates a docs site. We'll review lineage.

## Deliverables
- Models in `models/staging/` and `models/marts/`
- Tests in `models/tests/` or in model YAML
- Macro(s) in `macros/`
- Documentation (model/column descriptions)
- All CI checks (if configured) passing

## Timebox
Aim for **2–3 hours**. If you decide not to implement something, explain the trade‑off in your repo README or in comments.

## Tips for Success
- Read `source_data/DATA_SUMMARY.md` to understand the bonus funds logic and data structure
- See `DUCKDB_QUERIES.md` for examples of setting up dbt sources with Parquet files
- Remember: `cash_used` ≠ `entry_fee` (this matters for revenue!)
- Handle data quality issues in staging (use COALESCE, NULLIF, etc.)
- Filter to `status = 'completed'` for financial calculations
- Separate admin deposits from user deposits
- Document your time grain choice and incremental strategy rationale
- Test for both data quality and business logic

## Submission
1. **Create a Pull Request** in your private repository:
   * Title: `Submission: <Your Name>`
   * In the PR description, include:
     - Approx. time spent
     - Assumptions & edge cases
     - Any deviations from requirements with rationale
     - Anything you'd do with more time
2. **Grant repository access** to reviewers: `@eamon-underdog`, `@kimjam`, `@bagpipes1323`
3. **Open an Issue** on the [template repo](https://github.com/Underdog-Inc/dbt-takehome-template) titled `Submission: <Your Name>` with a link to your PR

## Rubric (what we look for)
- **Modeling & structure (30%)** — staging vs marts separation, naming, clarity, handling nuanced business context correctly
- **Testing (15%)** — appropriate tests and coverage, data quality tests
- **Documentation (10%)** — useful descriptions and READMEs
- **Incremental strategy (5%)** — correctness, idempotence, grain choice & rationale
- **SQL quality (10%)** — readability, maintainability, macro use
- **Execution (15%)** — commit hygiene, reproducible build, docs, handling data quality issues
- **Polish / Bonus (15%)** — thoughtful macros, weekly NFL-aligned model, additional mart models (contests/deposits/withdrawals), semantic layering

> It's okay to leave notes on "what I'd do next in production."
