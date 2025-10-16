# Seed Data Summary

## Overview
Synthetic fantasy sports data for Underdog Fantasy dbt take-home assessment covering the 2024 NFL season (September 2024 - January 2025). **Includes realistic scale and intentional data quality issues.**

## Quick Stats
| File | Rows | Description |
|------|------|-------------|
| `users.csv` | 5,000 | User accounts with signup info and KYC status |
| `contests.csv` | 500 | Fantasy contests with various types and entry fees |
| `entries.csv` | 75,000 | User entries into contests with bonus funds tracking |
| `deposits.csv` | 8,000 | User deposit transactions (includes ~15% admin/bonus deposits) |
| `withdrawals.csv` | 2,000 | User withdrawal transactions |

## Data Relationships
```
users (1) ──< (N) entries (N) >── (1) contests
  │                
  ├──< (N) deposits (includes admin/bonus deposits)
  │
  └──< (N) withdrawals
```

## Key Business Logic: Bonus Funds

**Admin Deposits:**
- Identified by `is_admin_deposit = TRUE` in `deposits.csv`
- Represent promotional/bonus funds credited to user accounts
- Always have `status = 'completed'` and empty `payment_method`
- Do NOT count as user cash deposits

**Bonus Fund Usage:**
- Tracked in `entries.csv` via `bonus_funds_used` and `cash_used` columns
- Bonus funds are consumed FIRST before user cash
- `entry_fee = bonus_funds_used + cash_used`
- **Only `cash_used` should count toward net gaming revenue**

**Example:**
```
User receives $50 bonus deposit (admin)
User deposits $100 cash
User enters $25 contest → uses $25 bonus (bonus_funds_used=25, cash_used=0)
User enters $40 contest → uses $25 bonus + $15 cash (bonus_funds_used=25, cash_used=15)
User enters $20 contest → uses $20 cash (bonus_funds_used=0, cash_used=20)
```

## Sample Business Metrics You Can Calculate

### User-Level Metrics (per period)
- `total_entries`: COUNT of entries
- `cash_entry_fees`: SUM of `cash_used` (NOT `entry_fee`!) ⚠️
- `bonus_entry_fees`: SUM of `bonus_funds_used`
- `payouts`: SUM of payouts won
- `net_gaming_revenue`: cash_entry_fees - payouts ⚠️ **Cash only!**
- `cash_deposits`: SUM of completed deposits WHERE is_admin_deposit = FALSE
- `withdrawals`: SUM of completed withdrawals
- `balance_change`: cash_deposits - withdrawals - cash_entry_fees + payouts
- `win_rate`: % of entries that resulted in payouts
- `avg_payout_when_winning`: Average payout for winning entries

### Contest-Level Metrics
- `fill_rate`: COUNT(entries) / max_entries
- `contest_revenue`: SUM of `cash_used` from entries
- `contest_margin`: contest_revenue - SUM of payouts
- `payout_rate`: SUM(payouts) / SUM(entry_fees)
- `avg_entry_fee`: Average entry fee by contest type
- `prize_pool_efficiency`: Total payouts / prize_pool

### Deposit/Withdrawal Metrics
- Success rate by payment method
- Average deposit/withdrawal amounts
- Admin deposit distribution
- Transaction failure analysis
- Deposits vs withdrawals (net deposits)

### Geographic Metrics
- Net gaming revenue by state (cash_used - payouts)
- User acquisition by state
- Active users by state
- Average revenue per user by state

## Data Quality Notes

⚠️ **Intentional Data Quality Issues (~1-2% of records):**
- Users: ~1% missing `state`, ~0.5% missing `signup_channel`
- Contests: ~1% missing `prize_pool`
- Entries: ~1% missing `payout_amount`
- Deposits: ~1% of non-admin deposits missing `payment_method`
- Withdrawals: ~0.5% missing `status`

**These are intentional to test:**
- Staging layer data cleaning (COALESCE, NULLIF, etc.)
- Data quality tests (not_null, accepted_values)
- Handling edge cases in aggregations

✅ **Realistic patterns:**
- Users must exist before they can make deposits/withdrawals
- Entry times are before contest start times
- Cancelled contests refund entry fees
- ~20% win rate on completed contests
- ~90% deposit success rate
- ~80% withdrawal completion rate
- Bonus funds consumed before cash

✅ **Edge cases included:**
- Failed transactions (deposits & withdrawals)
- Cancelled contests with refunds
- Inactive users
- Pending KYC statuses
- Admin/bonus deposits with no payment method
- Multiple contest types with varying economics
- Some contests may not fill to capacity

## Regenerating Data

To regenerate the seed data with different parameters:

```bash
python3 scripts/generate_seeds.py
```

Edit the script's configuration section to adjust:
- Number of records (users, contests, entries, etc.)
- Date ranges
- Win rates and payout multipliers
- Distribution of states, channels, etc.
