"""
Validate and summarize the generated seed data.
Quick sanity checks and statistics.
"""

import csv
from pathlib import Path
from collections import Counter
from datetime import datetime

seeds_dir = Path(__file__).parent.parent / 'seeds'

def load_csv(filename):
    """Load CSV file and return list of dicts."""
    with open(seeds_dir / filename, 'r') as f:
        return list(csv.DictReader(f))

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

# Load all data
users = load_csv('users.csv')
contests = load_csv('contests.csv')
entries = load_csv('entries.csv')
deposits = load_csv('deposits.csv')
withdrawals = load_csv('withdrawals.csv')

print_section("RECORD COUNTS")
print(f"Users:       {len(users):>6}")
print(f"Contests:    {len(contests):>6}")
print(f"Entries:     {len(entries):>6}")
print(f"Deposits:    {len(deposits):>6}")
print(f"Withdrawals: {len(withdrawals):>6}")

print_section("USERS - Distribution")
states = Counter(u['state'] for u in users)
print(f"\nTop 5 States:")
for state, count in states.most_common(5):
    print(f"  {state}: {count}")

channels = Counter(u['signup_channel'] for u in users)
print(f"\nSignup Channels:")
for channel, count in channels.most_common():
    print(f"  {channel}: {count}")

kyc = Counter(u['kyc_status'] for u in users)
print(f"\nKYC Status:")
for status, count in kyc.items():
    print(f"  {status}: {count}")

print_section("CONTESTS - Economics")
contest_types = Counter(c['contest_type'] for c in contests)
print(f"\nContest Types:")
for ctype, count in contest_types.most_common():
    print(f"  {ctype}: {count}")

completed = sum(1 for c in contests if c['status'] == 'completed')
cancelled = sum(1 for c in contests if c['status'] == 'cancelled')
print(f"\nContest Status:")
print(f"  completed: {completed}")
print(f"  cancelled: {cancelled}")

entry_fees = [float(c['entry_fee']) for c in contests]
print(f"\nEntry Fee Range: ${min(entry_fees):.0f} - ${max(entry_fees):.0f}")
print(f"Average Entry Fee: ${sum(entry_fees)/len(entry_fees):.2f}")

print_section("ENTRIES - Payouts")
total_entries = len(entries)
entries_with_payout = sum(1 for e in entries if float(e['payout_amount']) > 0)
print(f"\nTotal Entries: {total_entries}")
print(f"Entries with Payouts: {entries_with_payout}")
print(f"Win Rate: {entries_with_payout/total_entries*100:.1f}%")

total_entry_fees = sum(float(e['entry_fee']) for e in entries)
total_payouts = sum(float(e['payout_amount']) for e in entries)
print(f"\nTotal Entry Fees: ${total_entry_fees:,.2f}")
print(f"Total Payouts: ${total_payouts:,.2f}")
print(f"House Edge (Entry Fees - Payouts): ${total_entry_fees - total_payouts:,.2f}")

print_section("DEPOSITS - Financial")
deposit_statuses = Counter(d['status'] for d in deposits)
print(f"\nDeposit Status:")
for status, count in deposit_statuses.items():
    print(f"  {status}: {count}")

completed_deposits = [float(d['amount']) for d in deposits if d['status'] == 'completed']
print(f"\nCompleted Deposits: {len(completed_deposits)}")
print(f"Total Deposit Amount: ${sum(completed_deposits):,.2f}")
print(f"Average Deposit: ${sum(completed_deposits)/len(completed_deposits):.2f}")

payment_methods = Counter(d['payment_method'] for d in deposits)
print(f"\nPayment Methods:")
for method, count in payment_methods.most_common():
    print(f"  {method}: {count}")

print_section("WITHDRAWALS - Financial")
withdrawal_statuses = Counter(w['status'] for w in withdrawals)
print(f"\nWithdrawal Status:")
for status, count in withdrawal_statuses.items():
    print(f"  {status}: {count}")

completed_withdrawals = [float(w['amount']) for w in withdrawals if w['status'] == 'completed']
print(f"\nCompleted Withdrawals: {len(completed_withdrawals)}")
print(f"Total Withdrawal Amount: ${sum(completed_withdrawals):,.2f}")
print(f"Average Withdrawal: ${sum(completed_withdrawals)/len(completed_withdrawals):.2f}")

print_section("DATA QUALITY CHECKS")

# Check 1: All entry user_ids exist in users
user_ids = {u['user_id'] for u in users}
invalid_entries = [e for e in entries if e['user_id'] not in user_ids]
print(f"\n✓ All entries reference valid users: {len(invalid_entries) == 0}")

# Check 2: All entry contest_ids exist in contests
contest_ids = {c['contest_id'] for c in contests}
invalid_contests = [e for e in entries if e['contest_id'] not in contest_ids]
print(f"✓ All entries reference valid contests: {len(invalid_contests) == 0}")

# Check 3: Entry fees match contest entry fees
mismatched_fees = []
contest_fee_map = {c['contest_id']: float(c['entry_fee']) for c in contests}
for e in entries:
    if float(e['entry_fee']) != contest_fee_map[e['contest_id']]:
        mismatched_fees.append(e)
print(f"✓ All entry fees match contest fees: {len(mismatched_fees) == 0}")

# Check 4: Cancelled contests refund entry fee
cancelled_contest_ids = {c['contest_id'] for c in contests if c['status'] == 'cancelled'}
cancelled_entries = [e for e in entries if e['contest_id'] in cancelled_contest_ids]
incorrect_refunds = [e for e in cancelled_entries if float(e['payout_amount']) != float(e['entry_fee'])]
print(f"✓ Cancelled contests refund entry fees: {len(incorrect_refunds) == 0}")

# Check 5: All deposits/withdrawals reference valid users
invalid_deposits = [d for d in deposits if d['user_id'] not in user_ids]
invalid_withdrawals = [w for w in withdrawals if w['user_id'] not in user_ids]
print(f"✓ All deposits reference valid users: {len(invalid_deposits) == 0}")
print(f"✓ All withdrawals reference valid users: {len(invalid_withdrawals) == 0}")

print("\n" + "=" * 60)
print("  ✅ Data validation complete!")
print("=" * 60 + "\n")
