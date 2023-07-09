CREATE SOURCE trade (
  product_id varchar,
  type varchar,
  time timestamp,
  price real,
  last_size real,
  trade_id integer,
  bid real,
  bid_size real,
  ask real,
  ask_size real,
  spread real)
with ( connector = 'kafka', topic = 'trade', 
       properties.bootstrap.server = 'redpanda:9092', scan.startup.mode = 'earliest') 
ROW FORMAT JSON;


create materialized view oc as (
with minute_bar as (
  SELECT product_id, time, price, window_start, window_end
  FROM TUMBLE (trade, time, INTERVAL '1 MINUTES')
  ),
close_time as (
  select product_id as snapid, max(time) as snaptime from minute_bar
  group by product_id, window_end
),
open_time as (
  select product_id as snapid, min(time) as snaptime from minute_bar
  group by product_id, window_end
),
close as (
  select product_id, window_end as minute, price as close from minute_bar
  natural join close_time
  where time=snaptime and product_id=snapid
),
open as (
  select product_id, window_end as minute, price as open from minute_bar
  natural join open_time
  where time=snaptime and product_id=snapid
)
select * from close
natural join open);


create materialized view ohlcv as
with hl as (
  SELECT product_id, window_start, window_end as minute, min(price) as low, max(price) as high,
  sum(last_size) as volume
  FROM TUMBLE (trade, time, INTERVAL '1 MINUTES') 
  GROUP BY product_id, window_start, window_end 
  ORDER BY window_start ASC
)
select hl.product_id, hl.minute, oc.open, hl.high, hl.low, oc.close, hl.volume
from hl 
natural join oc;