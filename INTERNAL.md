# 🎯 Assessment Administrator Guide

## Overview

This is an Underdog Fantasy-themed dbt take-home assessment testing:
- **Technical Skills**: dbt modeling, testing, incremental strategies, data cleaning
- **Business Acumen**: Understanding bonus funds, revenue calculations, fantasy sports metrics
- **Scale**: 90,000+ records requiring thoughtful queries
- **Data Quality**: Intentional NULLs/missing values to test staging layer skills

**Expected Time**: 2-3 hours  
**Difficulty**: Intermediate to Advanced

---

## Dataset Overview

| File | Rows | Key Feature |
|------|------|-------------|
| `users.csv` | 5,000 | ~1% missing state/channel |
| `contests.csv` | 500 | ~1% missing prize_pool |
| `entries.csv` | 75,000 | Bonus funds tracking, ~1% missing payouts |
| `deposits.csv` | 8,000 | ~15% are admin/bonus deposits |
| `withdrawals.csv` | 2,000 | ~0.5% missing status |

**Data Period**: September 2024 - January 2025 (NFL season)

---

## 🔑 Critical Business Logic (The Main Test)

### Bonus Funds vs Cash Revenue

**THE KEY DISTINCTION:**
- Admin deposits (`is_admin_deposit = TRUE`) are promotional bonuses
- Bonus funds are consumed FIRST before user cash
- **Only cash entry fees count toward net gaming revenue**

**Example Flow:**
```
User receives $50 bonus + deposits $100 cash
→ Enters $25 contest: uses $25 bonus, $0 cash
→ Enters $40 contest: uses $25 bonus, $15 cash
→ Enters $20 contest: uses $0 bonus, $20 cash

Total entry fees = $85
But real revenue = only $35 (cash portion)
```

**Correct Revenue Calculation:**
```sql
-- ❌ WRONG - Overstates revenue by ~$57K
SELECT SUM(entry_fee) - SUM(payouts) AS net_revenue

-- ✅ CORRECT - Only count cash, not bonuses
SELECT SUM(cash_used) - SUM(payouts) AS net_revenue
```

**This is the #1 thing to check in submissions!**

---

## 📋 Evaluation Checklist

### Must-Haves (Will Fail Without)
- [ ] Staging models exist and handle NULLs properly
- [ ] **Uses `cash_used` NOT `entry_fee` for revenue calculations**
- [ ] At least one incremental model with strategy documented
- [ ] User-level periodic metrics model (daily/weekly/monthly)
- [ ] Top 10 states by net gaming revenue
- [ ] Basic tests (unique, not_null, relationships)
- [ ] Model/column descriptions in schema.yml
- [ ] `dbt build` runs successfully

### Strong Signals (Differentiate Good from Great)
- [ ] Correctly separates admin deposits from user deposits
- [ ] Handles all data quality issues (NULLs) in staging
- [ ] Built 1-2 additional mart models (contests/deposits/withdrawals)
- [ ] Custom business logic tests (bonus_funds ≤ entry_fee)
- [ ] Data quality tests (accepted_values for status fields)
- [ ] Tuesday-start weekly model for NFL alignment
- [ ] Thoughtful macros (not just boilerplate)
- [ ] Clear documentation of assumptions and trade-offs
- [ ] Good commit hygiene

### Red Flags (Immediate Concerns)
- [ ] Uses `entry_fee` instead of `cash_used` for revenue ⚠️ **CRITICAL**
- [ ] Ignores data quality issues (NULLs propagate to marts)
- [ ] No tests for bonus funds logic
- [ ] Poor or missing documentation
- [ ] Overly complex queries for the dataset size
- [ ] No incremental strategy explanation
- [ ] Failed to separate staging from marts
- [ ] Tests don't pass

---

## 🎯 Evaluation Rubric (Detailed)

### Modeling & Structure (20 points)
- **Excellent (18-20)**: Clean staging/marts separation, handles bonus funds correctly, logical naming, well-organized
- **Good (15-17)**: Proper separation, mostly correct logic, minor organizational issues
- **Needs Improvement (10-14)**: Some confusion between layers, revenue calculation errors
- **Poor (<10)**: No separation, incorrect bonus funds handling, disorganized

**Key Check**: Do they use `cash_used` for revenue? If not, major deduction.

### Testing (15 points)
- **Excellent (14-15)**: Comprehensive tests including data quality, business logic (bonus funds), relationships, custom tests
- **Good (12-13)**: Good coverage of basic tests, some custom tests
- **Needs Improvement (8-11)**: Only basic tests, missing data quality or business logic
- **Poor (<8)**: Minimal or no tests

### Documentation (10 points)
- **Excellent (9-10)**: Clear model descriptions, assumptions documented, trade-offs explained
- **Good (7-8)**: Basic descriptions, some assumptions
- **Needs Improvement (5-6)**: Minimal documentation
- **Poor (<5)**: No documentation

### Incremental Strategy (10 points)
- **Excellent (9-10)**: Correct implementation, clear explanation, handles late-arriving data
- **Good (7-8)**: Works correctly, basic explanation
- **Needs Improvement (5-6)**: Works but unclear why
- **Poor (<5)**: Incorrect or missing

### SQL Quality (5 points)
- **Excellent (5)**: Readable CTEs, good naming, efficient, uses macros well
- **Good (4)**: Clean SQL, some reusability
- **Needs Improvement (3)**: Works but hard to read
- **Poor (<3)**: Messy, inefficient

### Execution (25 points)
- **Excellent (23-25)**: Builds cleanly, handles data quality, good commits, docs site works, handles NULLs properly
- **Good (19-22)**: Builds successfully, decent git hygiene, handles most data quality issues
- **Needs Improvement (13-18)**: Builds with warnings, poor commits, some data quality issues unaddressed
- **Poor (<13)**: Doesn't build, ignores data quality

### Bonus & Polish (15 points)
- Tuesday-start weekly model (+5)
- Additional mart models beyond requirements (+3 each, max 6)
- Thoughtful macros (+2)
- Contest performance analysis (+2)

---

## 🚨 Common Mistakes to Watch For

### 1. Revenue Calculation Error (CRITICAL)
```sql
-- ❌ They did this (overstates by $57K):
SUM(entry_fee) - SUM(payouts)

-- ✅ Should be:
SUM(cash_used) - SUM(payouts)
```
**Impact**: If they miss this, cap score at 65/100 max.

### 2. Ignoring Data Quality
- NULLs in `payout_amount` causing aggregation issues
- Missing states/channels not handled in staging
- No COALESCE or default handling

### 3. Admin Deposits in User Metrics
```sql
-- ❌ Wrong - includes bonus deposits as user cash:
SUM(amount) WHERE status = 'completed'

-- ✅ Correct - excludes admin deposits:
SUM(amount) WHERE status = 'completed' AND is_admin_deposit = FALSE
```

### 4. No Business Logic Tests
Should test:
- `bonus_funds_used <= entry_fee`
- `cash_used = entry_fee - bonus_funds_used`
- Contest payouts don't exceed prize pool

### 5. Poor Incremental Strategy
- No explanation of unique_key choice
- Doesn't handle late-arriving data
- No consideration of full refresh needs

---

## 📊 Quick Verification Queries

Run these against their submission to verify correctness:

### Check Bonus Funds Handling
```sql
-- Should be ~$2.5M (cash only), NOT ~$2.58M (entry_fee)
SELECT SUM(cash_used) AS cash_revenue
FROM {{ ref('stg_entries') }}
WHERE status = 'completed';
```

### Check Admin Deposit Separation
```sql
-- Should be ~6,800 deposits, NOT 8,000
SELECT COUNT(*) AS user_deposits
FROM {{ ref('stg_deposits') }}
WHERE status = 'completed' 
  AND is_admin_deposit = FALSE;
```

### Check Data Quality Handling
```sql
-- Should be 0 NULLs if staging layer is correct
SELECT COUNT(*) AS null_payouts
FROM {{ ref('stg_entries') }}
WHERE payout_amount IS NULL;
```

---

## 🔄 Regenerating Data (If Needed)

```bash
# If you need to refresh the seed data
cd /path/to/dbt-takehome-template
python3 scripts/generate_seeds.py

# Validate the generated data
python3 scripts/validate_seeds.py
```

**Note**: Data is deterministic (random seed = 42), so regeneration produces identical results.

---

## ⏱️ Typical Candidate Timeline

- **30-45 min**: Read docs, understand data, plan approach
- **45-60 min**: Build staging models, handle data quality
- **45-60 min**: Build marts, implement incremental strategy
- **15-30 min**: Add tests
- **15-30 min**: Documentation, cleanup, final checks

**Total**: 2.5-3.5 hours for thorough completion

---

## ✅ Final Submission Checklist

When reviewing, ensure:
1. [ ] Repository includes all required files
2. [ ] `dbt build` runs without errors
3. [ ] Revenue calculations use `cash_used` not `entry_fee`
4. [ ] Admin deposits separated from user deposits
5. [ ] Data quality issues handled in staging
6. [ ] At least one incremental model
7. [ ] Basic tests pass
8. [ ] Documentation exists
9. [ ] Can answer: "Why did you choose this time grain?"
10. [ ] Can answer: "How did you handle bonus funds in revenue?"
