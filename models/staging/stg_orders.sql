with src as (
  select * from {{ ref('orders') }}
),
clean as (
  select
    order_id,
    customer_id,
    {{ safe_cast('order_ts', 'timestamp') }} as order_ts,
    {{ safe_cast('amount', 'numeric') }} as amount,
    lower(status) as status
  from src
)
select * from clean