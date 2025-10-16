{{
  config(
    materialized='incremental',
    unique_key=['month', 'customer_id']
  )
}}

with orders as (
  select * from {{ ref('stg_orders') }} where status = 'completed'
),
by_month as (
  select
    date_trunc('month', order_ts) as month,
    customer_id,
    count(*) as order_count,
    sum(amount) as revenue
  from orders
  group by 1,2
)
select * from by_month

{% if is_incremental() %}
  -- Only keep new/updated months in incremental runs
  where month >= (select coalesce(max(month), '1900-01-01') from {{ this }})
{% endif %}