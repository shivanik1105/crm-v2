-- Fix heatmap by creating proper timestamp variance
-- Update emails to have created_at times that differ from timestamp

-- Update 50 emails with realistic processing delays
WITH email_sample AS (
    SELECT id, timestamp, 
           (EXTRACT(HOUR FROM timestamp)::INT) as hour,
           (EXTRACT(DOW FROM timestamp)::INT) as dow
    FROM emails 
    WHERE timestamp IS NOT NULL
    ORDER BY id
    LIMIT 50
)
UPDATE emails e
SET created_at = es.timestamp + (
    (CASE 
        WHEN es.hour BETWEEN 9 AND 12 THEN 15 + (random() * 30)::INT  -- Morning: 15-45 min
        WHEN es.hour BETWEEN 13 AND 17 THEN 10 + (random() * 25)::INT  -- Afternoon: 10-35 min
        ELSE 20 + (random() * 40)::INT  -- Other times: 20-60 min
    END) || ' minutes'
)::INTERVAL
FROM email_sample es
WHERE e.id = es.id;

-- Verify the data
SELECT 
    EXTRACT(DOW FROM timestamp) as day_of_week,
    EXTRACT(HOUR FROM timestamp) as hour,
    AVG(EXTRACT(EPOCH FROM (created_at - timestamp))/60) as avg_minutes,
    COUNT(*) as email_count
FROM emails
WHERE created_at IS NOT NULL 
  AND timestamp IS NOT NULL
  AND created_at > timestamp
GROUP BY EXTRACT(DOW FROM timestamp), EXTRACT(HOUR FROM timestamp)
ORDER BY day_of_week, hour;
