# DuckDB Query Reference

This guide provides examples for querying the Fantasy Sports data using DuckDB.

## Quick Start

### Query CSV files directly (no seeding required)
Use `uvx duckdb` to run SQL queries directly against CSV files:
```bash
# Count users by state
uvx duckdb -c "
  SELECT state, COUNT(*) as user_count
  FROM 'seeds/users.csv'
  GROUP BY state
  ORDER BY user_count DESC
  LIMIT 10;
"
```

> **Note:** `uvx duckdb` automatically installs the DuckDB CLI on first use—no separate installation needed!

### Use the interactive DuckDB CLI
```bash
# Open the seeded database
uvx duckdb ./.dbt/dbt_duckdb.duckdb

# Or query CSV files directly in one-liner mode
uvx duckdb -c "SELECT * FROM 'seeds/users.csv' LIMIT 10;"
```

## Common Query Examples

All examples below can be run with `uvx duckdb -c "..."` or in the interactive CLI (`uvx duckdb ./.dbt/dbt_duckdb.duckdb`).

### User Analysis
```sql
-- Users by signup channel
SELECT signup_channel, COUNT(*) as users, 
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct
FROM 'seeds/users.csv'
GROUP BY signup_channel;

-- KYC completion rate by state
SELECT state,
       COUNT(*) as total_users,
       SUM(CASE WHEN kyc_status = 'verified' THEN 1 ELSE 0 END) as verified,
       ROUND(100.0 * SUM(CASE WHEN kyc_status = 'verified' THEN 1 ELSE 0 END) / COUNT(*), 2) as verification_rate
FROM 'seeds/users.csv'
GROUP BY state
ORDER BY total_users DESC
LIMIT 10;
```

### Contest Analysis
```sql
-- Contest types and entry fees
SELECT contest_type,
       COUNT(*) as contest_count,
       AVG(entry_fee) as avg_entry_fee,
       SUM(max_entries) as total_capacity
FROM 'seeds/contests.csv'
WHERE status = 'completed'
GROUP BY contest_type;
```

## DuckDB Tips

### Performance
```sql
-- Use LIMIT for exploration
SELECT * FROM 'seeds/entries.csv' LIMIT 100;

-- Count rows quickly
SELECT COUNT(*) FROM 'seeds/users.csv';

-- Profile query performance
EXPLAIN SELECT * FROM 'seeds/entries.csv';
```

### Data Quality Checks
```sql
-- Check for NULLs
SELECT 
    COUNT(*) as total_rows,
    SUM(CASE WHEN state IS NULL THEN 1 ELSE 0 END) as null_states
FROM 'seeds/users.csv';

```

### Export Results
```sql
-- Export to CSV
COPY (
    SELECT state, COUNT(*) as user_count
    FROM 'seeds/users.csv'
    GROUP BY state
) TO 'output/users_by_state.csv' WITH (HEADER TRUE, DELIMITER ',');
```

## Interactive CLI Commands

When in the DuckDB CLI (`uvx duckdb ./.dbt/dbt_duckdb.duckdb`):

```
.help               -- Show all commands
.tables             -- List all tables
.schema TABLE_NAME  -- Show table schema
.mode markdown      -- Set output to markdown format
.mode csv           -- Set output to CSV format
.output file.csv    -- Redirect output to file
.read query.sql     -- Execute SQL from file
.quit               -- Exit
```

## Resources

- [DuckDB SQL Documentation](https://duckdb.org/docs/sql/introduction)
- [DuckDB CSV Reader](https://duckdb.org/docs/data/csv/overview)
- [DuckDB CLI Guide](https://duckdb.org/docs/api/cli)
