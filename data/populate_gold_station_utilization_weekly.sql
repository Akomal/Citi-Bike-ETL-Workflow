CREATE OR REPLACE TABLE lake_gold.gold_station_utilization_weekly AS
WITH daily_data AS (
  SELECT
    station_id,
    network_id,
    DATE(timestamp) AS date,
    free_bikes,
    empty_slots,
    LAG(free_bikes) OVER (PARTITION BY station_id, DATE(timestamp) ORDER BY timestamp) AS prev_free_bikes,
    is_station_full,
    is_station_empty,
    TIMESTAMP_TRUNC(timestamp, HOUR) AS hour
  FROM lake_silver.master_bike_station_status
),
aggregated_daily AS (
  SELECT
    station_id,
    network_id,
    date,
    COUNTIF(is_station_full) / COUNT(*) > 0.8 AS is_frequently_full,
    COUNTIF(is_station_empty) / COUNT(*) > 0.8 AS is_frequently_empty,
    AVG(free_bikes) AS avg_free_bikes,
    AVG(empty_slots) AS avg_empty_slots,
    SUM(CASE WHEN free_bikes < prev_free_bikes THEN 1 ELSE 0 END) AS total_check_outs,
    SUM(CASE WHEN free_bikes > prev_free_bikes THEN 1 ELSE 0 END) AS total_check_ins,
    ARRAY_AGG(hour ORDER BY (free_bikes + empty_slots) DESC LIMIT 1)[OFFSET(0)] AS peak_hour
  FROM daily_data
  GROUP BY station_id, network_id, date
),
weekly_aggregated AS (
  SELECT
    station_id,
    network_id,
    DATE_TRUNC(date, WEEK(MONDAY)) AS week_start,
    DATE_TRUNC(date, WEEK(MONDAY)) + 6 AS week_end,
    ANY_VALUE(is_frequently_full) AS is_frequently_full,
    ANY_VALUE(is_frequently_empty) AS is_frequently_empty,
    AVG(avg_free_bikes) AS avg_free_bikes,
    AVG(avg_empty_slots) AS avg_empty_slots,
    SUM(total_check_outs) AS total_check_outs,
    SUM(total_check_ins) AS total_check_ins,
    ARRAY_AGG(peak_hour ORDER BY peak_hour LIMIT 1)[OFFSET(0)] AS most_common_peak_hour
  FROM aggregated_daily
  GROUP BY station_id, network_id, week_start, week_end
)
SELECT * FROM weekly_aggregated;

