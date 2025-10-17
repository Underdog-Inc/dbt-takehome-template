-- Example staging model for entries
-- This demonstrates handling data quality issues and type casting

with source as (
    select * from {{ source('raw_data', 'entries') }}
),

cleaned as (
    select
        entry_id,
        user_id,
        contest_id,
        cast(entry_time as timestamp) as entry_time,
        cast(entry_fee as numeric) as entry_fee,
        cast(bonus_funds_used as numeric) as bonus_funds_used,
        cast(cash_used as numeric) as cash_used,
        -- Handle NULL payout_amount (data quality issue)
        coalesce(nullif(payout_amount, ''), '0')::numeric as payout_amount,
        lower(trim(status)) as status
    from source
)

select * from cleaned
