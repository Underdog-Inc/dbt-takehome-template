# DuckDB Query Reference

This guide provides examples for querying the Fantasy Sports data using DuckDB.

## Quick Start

Use `uvx` to run DuckDB queries directly without any setup:

### Query Parquet files directly
```bash
# Count users by state
uvx duckdb -c "SELECT state, COUNT(*) as user_count 
  FROM 'source_data/users.parquet' 
  WHERE state IS NOT NULL 
  GROUP BY state 
  ORDER BY user_count DESC 
  LIMIT 10"
```

### Query your dbt database
```bash
# View all tables in your dbt database (after running dbt run)
uvx duckdb ./.dbt/dbt_duckdb.duckdb -c "SHOW TABLES"

# Query a specific model
uvx duckdb ./.dbt/dbt_duckdb.duckdb -c "SELECT * FROM stg_users LIMIT 10"
```

### Interactive DuckDB CLI
```bash
# Open interactive session with Parquet files
uvx duckdb

# Or open your dbt database interactively
uvx duckdb ./.dbt/dbt_duckdb.duckdb
```

## Setting Up dbt Sources

To use these Parquet files as sources in dbt, create a `_sources.yml` file in `models/staging/`:

```yaml
version: 2

sources:
  - name: raw_data
    description: Raw Parquet source files
    meta:
      external: true
    
    tables:
      - name: entries
        description: User accounts and KYC information
        meta:
          external_location: "read_parquet('source_data/entries.parquet')"
```

Then use in your models:

```sql
-- models/staging/stg_users.sql
select * from {{ source('raw_data', 'users') }}
```

## Common Query Examples

All examples below can be run with `uvx duckdb -c "YOUR_QUERY"` or in the interactive CLI.

### User Analysis
```sql
-- Users by signup channel
SELECT signup_channel, COUNT(*) as users, 
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct
FROM 'source_data/users.parquet'
WHERE signup_channel IS NOT NULL AND signup_channel != ''
GROUP BY signup_channel
ORDER BY users DESC;

-- KYC status breakdown (important: only verified users can transact!)
SELECT kyc_status,
       COUNT(*) as user_count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct,
       SUM(CASE WHEN state IS NOT NULL AND state != '' THEN 1 ELSE 0 END) as users_with_state
FROM 'source_data/users.parquet'
GROUP BY kyc_status
ORDER BY user_count DESC;

-- Top 10 states by verified user count
SELECT state,
       COUNT(*) as verified_users
FROM 'source_data/users.parquet'
WHERE state IS NOT NULL AND state != '' AND kyc_status = 'verified'
GROUP BY state
ORDER BY verified_users DESC
LIMIT 10;
```

### Contest Analysis
```sql
-- Contest types and entry fees
SELECT contest_type,
       COUNT(*) as contest_count,
       AVG(entry_fee) as avg_entry_fee,
       SUM(max_entries) as total_capacity
FROM 'source_data/contests.parquet'
WHERE status = 'completed'
GROUP BY contest_type;
```

## DuckDB Tips

### Performance
```bash
# Use LIMIT for exploration
uvx duckdb -c "SELECT * FROM 'source_data/entries.parquet' LIMIT 100"

# Count rows quickly
uvx duckdb -c "SELECT COUNT(*) FROM 'source_data/users.parquet'"

# Profile query performance
uvx duckdb -c "EXPLAIN SELECT * FROM 'source_data/entries.parquet'"
```

### Data Quality Checks
```bash
# Check for NULLs
uvx duckdb -c "SELECT 
    COUNT(*) as total_rows,
    SUM(CASE WHEN state IS NULL THEN 1 ELSE 0 END) as null_states
FROM 'source_data/users.parquet'"
```

### Export Results
```bash
# Export to CSV
uvx duckdb -c "COPY (
    SELECT state, COUNT(*) as user_count
    FROM 'source_data/users.parquet'
    GROUP BY state
) TO 'output/users_by_state.csv' WITH (HEADER TRUE, DELIMITER ',')"
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
