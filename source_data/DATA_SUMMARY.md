# Source Data Summary

## Overview
Synthetic fantasy sports data for Underdog Fantasy dbt take-home assessment covering the 2024 NFL season (September 2024 - January 2025). **Includes realistic scale, NFL weekly seasonality patterns, and intentional data quality issues.**

All data is stored in **Parquet format** for efficient storage and fast querying with DuckDB.

## Quick Stats
| File | Rows | Description |
|------|------|-------------|
| `users.parquet` | 40,000 | User accounts with signup info and KYC status |
| `contests.parquet` | 4,000 | Fantasy contests with various types and entry fees |
| `entries.parquet` | 600,000 | User entries into contests with bonus funds tracking |
| `deposits.parquet` | 64,000 | User deposit transactions (includes ~15% admin/bonus deposits) |
| `withdrawals.parquet` | 16,000 | User withdrawal transactions |

**Total size: ~37 MB** (compressed with Snappy)

## Data Characteristics

### ID Format
All ID fields use **UUIDs** (e.g., `f4a06ec5-a762-459b-9413-8fc28b08d505`) instead of sequential integers:
- `user_id`
- `contest_id`
- `entry_id`
- `deposit_id`
- `withdrawal_id`

### NFL Weekly Seasonality
Activity timestamps (contests, deposits, entries, withdrawals) follow realistic NFL weekly patterns:
- **Sunday**: ~40% of weekly activity (NFL game day)
- **Thursday**: ~15% of activity (Thursday Night Football)
- **Monday**: ~15% of activity (Monday Night Football)
- **Saturday**: ~10% of activity (College football)
- **Other weekdays**: ~20% of activity (distributed across Tue/Wed/Fri)

### KYC Verification Requirements (Important!)
To mimic real-world regulatory requirements:
- 🔐 **Only verified users (`kyc_status = 'verified'`) can:**
  - Make deposits
  - Make withdrawals  
  - Enter contests
- 📍 **Only verified users have state information**
  - Unverified/pending users have NULL state until KYC is complete
- 📊 **User Distribution:**
  - ~60% verified users (can transact)
  - ~40% pending/unverified users (cannot transact, no state data)

**This is a business rule, not a data quality issue!** When filtering for active users or calculating metrics, you'll typically want to focus on verified users.

## Data Relationships
```
users (1) ──< (N) entries (N) >── (1) contests
  │                
  ├──< (N) deposits (includes admin/bonus deposits)
  │
  └──< (N) withdrawals
```

## Schema Details

### `users.parquet`
| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `user_id` | STRING (UUID) | Unique user identifier | Primary key |
| `created_at` | TIMESTAMP | Account creation timestamp | |
| `state` | STRING | US state code (2 letters) | NULL for unverified/pending users |
| `signup_channel` | STRING | How user signed up | ~0.5% NULL (data quality issue) |
| `kyc_status` | STRING | KYC verification status | `verified`, `pending`, or `unverified` |

### `contests.parquet`
| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `contest_id` | STRING (UUID) | Unique contest identifier | Primary key |
| `contest_type` | STRING | Type of fantasy contest | `best_ball`, `snake_draft`, `salary_cap`, `survivor` |
| `entry_fee` | DECIMAL | Cost to enter contest | 5, 10, 20, 25, 50, or 100 |
| `start_time` | TIMESTAMP | Contest start time | Follows NFL seasonality |
| `status` | STRING | Contest status | `completed` (90%), `cancelled` (10%) |
| `max_entries` | INTEGER | Maximum number of entries | 10, 20, 50, 100, 500, or 1000 |
| `prize_pool` | DECIMAL | Total prize money | ~0.5% NULL (data quality issue) |

### `entries.parquet`
| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `entry_id` | STRING (UUID) | Unique entry identifier | Primary key |
| `user_id` | STRING (UUID) | User who made entry | Foreign key to `users` |
| `contest_id` | STRING (UUID) | Contest entered | Foreign key to `contests` |
| `entry_time` | TIMESTAMP | When entry was made | Follows NFL seasonality |
| `entry_fee` | DECIMAL | Total fee paid | `cash_used + bonus_funds_used` |
| `bonus_funds_used` | DECIMAL | Amount of bonus funds used | ≥ 0, ≤ entry_fee |
| `cash_used` | DECIMAL | Amount of cash used | ≥ 0, ≤ entry_fee |
| `payout_amount` | DECIMAL | Winnings from this entry | NULL if no payout, 0 if lost |
| `status` | STRING | Entry status | Matches contest status |

**Important**: `entry_fee = cash_used + bonus_funds_used`. Revenue should be calculated from `cash_used` only, not `entry_fee`!

### `deposits.parquet`
| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `deposit_id` | STRING (UUID) | Unique deposit identifier | Primary key |
| `user_id` | STRING (UUID) | User making deposit | Foreign key to `users` |
| `deposit_ts` | TIMESTAMP | Deposit timestamp | Follows NFL seasonality |
| `amount` | DECIMAL | Deposit amount | Positive number |
| `payment_method` | STRING | Payment method used | `credit_card`, `debit_card`, `paypal`, `venmo`, `bank_transfer` |
| `status` | STRING | Deposit status | `completed`, `pending`, `failed`, `cancelled` |
| `is_admin_deposit` | BOOLEAN | Admin/bonus deposit flag | TRUE for ~15% of deposits |

**Important**: Admin deposits (bonus funds) should be excluded from user deposit metrics.

### `withdrawals.parquet`
| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `withdrawal_id` | STRING (UUID) | Unique withdrawal identifier | Primary key |
| `user_id` | STRING (UUID) | User making withdrawal | Foreign key to `users` |
| `withdrawal_ts` | TIMESTAMP | Withdrawal timestamp | Follows NFL seasonality |
| `amount` | DECIMAL | Withdrawal amount | Positive number |
| `status` | STRING | Withdrawal status | `completed`, `pending`, `failed`, `cancelled` |

## Data Quality Issues

The data intentionally includes realistic data quality issues (~1-2% of records):

1. **NULL States**: Unverified/pending users have NULL `state` (this is a business rule, not a bug!)
2. **NULL Signup Channels**: ~0.5% of users have NULL `signup_channel` (data quality issue)
3. **NULL Prize Pools**: ~0.5% of contests have NULL `prize_pool` (data quality issue)
4. **Failed Transactions**: Some deposits and withdrawals have `status` = 'failed' or 'cancelled'

These should be handled in your staging models with appropriate COALESCE, NULLIF, or filtering logic.

## Bonus Funds Logic

Bonus funds are tracked through:
1. **Admin deposits** (`is_admin_deposit = TRUE` in `deposits`) add bonus funds to user accounts
2. **Entry bonus usage** (`bonus_funds_used` in `entries`) tracks how much bonus was used per entry
3. **Revenue calculation**: Use `cash_used`, NOT `entry_fee`, for revenue metrics

Example:
- User receives $25 admin deposit (bonus funds)
- User enters $10 contest using $5 cash + $5 bonus
- Revenue from this entry = $5 (cash_used), not $10 (entry_fee)

## Using These Files with dbt

These Parquet files should be configured as **external sources** in dbt. See the main documentation for examples of how to set up source configurations with dbt-duckdb.

Example source configuration (add to `models/staging/_sources.yml`):

```yaml
version: 2

sources:
  - name: raw_data
    description: Raw Parquet source files
    
    tables:
      - name: users
        description: User accounts and KYC information
        meta:
          external_location: "read_parquet('source_data/users.parquet')"
```

Then reference in your models:

```sql
select * from {{ source('raw_data', 'users') }}
```
