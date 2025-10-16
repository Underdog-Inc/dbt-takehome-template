"""
Generate synthetic fantasy sports data for dbt take-home assessment.
Creates CSV seed files for users, contests, entries, deposits, and withdrawals.
Includes bonus funds logic and intentional data quality issues.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Set seed for reproducibility
random.seed(42)

# Configuration - MUCH LARGER DATASET
NUM_USERS = 5000
NUM_CONTESTS = 500
NUM_ENTRIES = 75000
NUM_DEPOSITS = 8000
NUM_WITHDRAWALS = 2000

# Reference data
STATES = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI', 
          'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI']
SIGNUP_CHANNELS = ['organic', 'paid_social', 'referral', 'influencer', 'email', 'seo']
KYC_STATUS = ['verified', 'pending', 'unverified']
CONTEST_TYPES = ['pick_em', 'best_ball', 'snake_draft', 'salary_cap', 'survivor']
PAYMENT_METHODS = ['credit_card', 'debit_card', 'paypal', 'venmo', 'bank_transfer']
STATUSES = ['completed', 'pending', 'failed', 'cancelled']

# Helper functions
def random_date(start_date, end_date):
    """Generate a random datetime between start_date and end_date."""
    time_between = end_date - start_date
    random_seconds = random.randint(0, int(time_between.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

def format_timestamp(dt):
    """Format datetime as ISO string."""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# Date ranges
START_DATE = datetime(2024, 9, 1)  # NFL season start
END_DATE = datetime(2025, 1, 31)   # Through conference championships

# Generate Users
print("Generating users...")
users = []
for i in range(1, NUM_USERS + 1):
    created_at = random_date(START_DATE - timedelta(days=365), START_DATE)
    
    # Introduce some data quality issues (~2% of records)
    state = random.choice(STATES) if random.random() > 0.01 else None
    signup_channel = random.choice(SIGNUP_CHANNELS) if random.random() > 0.005 else None
    
    users.append({
        'user_id': i,
        'created_at': format_timestamp(created_at),
        'state': state if state else '',  # NULL as empty string in CSV
        'signup_channel': signup_channel if signup_channel else '',
        'kyc_status': random.choice(KYC_STATUS),
        'is_active': random.choice([True, False]) if random.random() > 0.2 else True,
    })

# Generate Contests
print("Generating contests...")
contests = []
for i in range(1, NUM_CONTESTS + 1):
    contest_type = random.choice(CONTEST_TYPES)
    entry_fee = random.choice([5, 10, 20, 25, 50, 100])
    max_entries = random.choice([10, 20, 50, 100, 500, 1000])
    start_time = random_date(START_DATE, END_DATE)
    
    # Most contests are completed, some are cancelled
    if random.random() > 0.1:
        status = 'completed'
    else:
        status = 'cancelled'
    
    # Some data quality issues - missing prize pool (~0.5%)
    prize_pool = entry_fee * random.randint(5, max_entries // 2) if random.random() > 0.005 else None
    
    contests.append({
        'contest_id': i,
        'contest_type': contest_type,
        'entry_fee': entry_fee,
        'start_time': format_timestamp(start_time),
        'status': status,
        'max_entries': max_entries,
        'prize_pool': prize_pool if prize_pool is not None else '',
    })

# Generate Deposits (including admin/bonus deposits) - BEFORE ENTRIES
print("Generating deposits...")
deposits = []
user_bonus_balances = {}  # Track bonus funds per user

for i in range(1, NUM_DEPOSITS + 1):
    user = random.choice(users)
    user_id = user['user_id']
    deposit_time = random_date(
        datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S'),
        END_DATE
    )
    
    # 15% of deposits are admin/bonus deposits
    is_admin = random.random() < 0.15
    
    if is_admin:
        amount = random.choice([10, 25, 50, 100])  # Smaller bonus amounts
        payment_method = ''  # Admin deposits don't have payment method
        status = 'completed'  # Admin deposits always complete
        # Track bonus balance
        user_bonus_balances[user_id] = user_bonus_balances.get(user_id, 0) + amount
    else:
        amount = random.choice([25, 50, 100, 200, 500, 1000])
        payment_method = random.choice(PAYMENT_METHODS)
        status = random.choice(['completed'] * 9 + ['failed'])  # 90% success rate
        
        # Some data quality issues in payment_method (~1%)
        if random.random() < 0.01:
            payment_method = ''
    
    deposits.append({
        'deposit_id': i,
        'user_id': user_id,
        'deposit_ts': format_timestamp(deposit_time),
        'amount': amount,
        'payment_method': payment_method,
        'status': status,
        'is_admin_deposit': is_admin,
    })

# Sort deposits by time for chronological bonus balance tracking
sorted_deposits = sorted(deposits, key=lambda x: x['deposit_ts'])

# Rebuild bonus balances chronologically
user_bonus_balances = {}
for dep in sorted_deposits:
    if dep['is_admin_deposit'] and dep['status'] == 'completed':
        user_id = dep['user_id']
        user_bonus_balances[user_id] = user_bonus_balances.get(user_id, 0) + dep['amount']

# Generate Entries (with bonus funds usage)
print("Generating entries...")
entries = []
entry_id = 1

# Sort deposits by time to properly track bonus balances
sorted_deposits = sorted(deposits, key=lambda x: x['deposit_ts'])

# Rebuild bonus balances chronologically
user_bonus_balances = {}
for dep in sorted_deposits:
    if dep['is_admin_deposit'] and dep['status'] == 'completed':
        user_id = dep['user_id']
        user_bonus_balances[user_id] = user_bonus_balances.get(user_id, 0) + dep['amount']

for i in range(NUM_ENTRIES):
    user = random.choice(users)
    user_id = user['user_id']
    contest = random.choice(contests)
    entry_fee = contest['entry_fee']
    
    # Entry time should be before contest start
    contest_start = datetime.strptime(contest['start_time'], '%Y-%m-%d %H:%M:%S')
    entry_time = random_date(
        contest_start - timedelta(hours=48),
        contest_start
    )
    
    # Bonus funds are used first
    user_bonus = user_bonus_balances.get(user_id, 0)
    if user_bonus > 0:
        bonus_funds_used = min(user_bonus, entry_fee)
        user_bonus_balances[user_id] = user_bonus - bonus_funds_used
    else:
        bonus_funds_used = 0
    
    # Calculate cash portion
    cash_used = entry_fee - bonus_funds_used
    
    # Payout calculation
    if contest['status'] == 'completed':
        # 20% chance of winning with varied payout amounts
        if random.random() < 0.2:
            payout_multiplier = random.choice([1.5, 2, 3, 5, 10, 20])
            payout_amount = round(entry_fee * payout_multiplier, 2)
        else:
            payout_amount = 0
    else:
        # Cancelled contests refund entry fee
        payout_amount = entry_fee
    
    # Some data quality issues (~1% have NULL payout_amount)
    if random.random() < 0.01:
        payout_amount = None
    
    entries.append({
        'entry_id': entry_id,
        'user_id': user_id,
        'contest_id': contest['contest_id'],
        'entry_time': format_timestamp(entry_time),
        'entry_fee': entry_fee,
        'bonus_funds_used': bonus_funds_used,
        'cash_used': cash_used,
        'payout_amount': payout_amount if payout_amount is not None else '',
        'status': 'completed' if contest['status'] == 'completed' else contest['status'],
    })
    entry_id += 1

# Generate Withdrawals
print("Generating withdrawals...")
withdrawals = []
for i in range(1, NUM_WITHDRAWALS + 1):
    user = random.choice(users)
    withdrawal_time = random_date(
        datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S') + timedelta(days=7),
        END_DATE
    )
    amount = random.choice([50, 100, 200, 500, 1000, 2000])
    status = random.choice(['completed'] * 8 + ['pending', 'failed'])  # 80% completed
    
    # Some data quality issues - missing status (~0.5%)
    if random.random() < 0.005:
        status = ''
    
    withdrawals.append({
        'withdrawal_id': i,
        'user_id': user['user_id'],
        'withdrawal_ts': format_timestamp(withdrawal_time),
        'amount': amount,
        'status': status,
    })

# Write CSV files
print("\nWriting CSV files...")
seeds_dir = Path(__file__).parent.parent / 'seeds'
seeds_dir.mkdir(exist_ok=True)

# Write users.csv
with open(seeds_dir / 'users.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['user_id', 'created_at', 'state', 'signup_channel', 'kyc_status', 'is_active'])
    writer.writeheader()
    writer.writerows(users)

# Write contests.csv
with open(seeds_dir / 'contests.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['contest_id', 'contest_type', 'entry_fee', 'start_time', 'status', 'max_entries', 'prize_pool'])
    writer.writeheader()
    writer.writerows(contests)

# Write entries.csv
with open(seeds_dir / 'entries.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['entry_id', 'user_id', 'contest_id', 'entry_time', 'entry_fee', 'bonus_funds_used', 'cash_used', 'payout_amount', 'status'])
    writer.writeheader()
    writer.writerows(entries)

# Write deposits.csv
with open(seeds_dir / 'deposits.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['deposit_id', 'user_id', 'deposit_ts', 'amount', 'payment_method', 'status', 'is_admin_deposit'])
    writer.writeheader()
    writer.writerows(deposits)

# Write withdrawals.csv
with open(seeds_dir / 'withdrawals.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['withdrawal_id', 'user_id', 'withdrawal_ts', 'amount', 'status'])
    writer.writeheader()
    writer.writerows(withdrawals)

print(f"\n✅ Generated seed data:")
print(f"   - users.csv: {NUM_USERS:,} rows")
print(f"   - contests.csv: {NUM_CONTESTS:,} rows")
print(f"   - entries.csv: {NUM_ENTRIES:,} rows")
print(f"   - deposits.csv: {NUM_DEPOSITS:,} rows")
print(f"   - withdrawals.csv: {NUM_WITHDRAWALS:,} rows")
print(f"\nFiles saved to: {seeds_dir}")
print(f"\n📊 Data characteristics:")
bonus_users = len([v for v in user_bonus_balances.values() if v > 0])
if bonus_users > 0:
    avg_bonus = sum(user_bonus_balances.values()) / bonus_users
    print(f"   - Admin/bonus deposits: ~15% of deposits")
    print(f"   - Users with bonus funds: {bonus_users:,}")
    print(f"   - Average bonus per user (with bonuses): ${avg_bonus:.2f}")
print(f"   - Data quality issues: ~1-2% of records have NULLs or missing values")
