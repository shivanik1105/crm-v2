-- Populate Actions table with sample response times to create heatmap data
-- This simulates replied emails across different days and hours

-- Get some email IDs to create actions for
DO $$
DECLARE
    email_record RECORD;
    response_time INTERVAL;
    day_offset INT;
    hour_val INT;
BEGIN
    FOR email_record IN 
        SELECT id, timestamp 
        FROM emails 
        WHERE status IN ('Drafted', 'Replied')
        LIMIT 30
    LOOP
        -- Random day offset (0-6 for past week)
        day_offset := floor(random() * 7)::INT;
        -- Random hour (business hours 8-18)
        hour_val := 8 + floor(random() * 11)::INT;
        
        -- Random response time (5-60 minutes)
        response_time := (5 + floor(random() * 55)::INT || ' minutes')::INTERVAL;
        
        -- Insert action with timestamp
        INSERT INTO actions (
            id,
            email_id,
            action_type,
            executed_at,
            reasoning,
            status
        ) VALUES (
            gen_random_uuid(),
            email_record.id,
            'auto_reply',
            email_record.timestamp + response_time,
            '{"decision": "auto_reply", "confidence": 0.9}',
            'completed'
        ) ON CONFLICT DO NOTHING;
    END LOOP;
END $$;

-- Verify data was inserted
SELECT 
    to_char(executed_at, 'Dy') as day,
    EXTRACT(HOUR FROM executed_at)::INT as hour,
    COUNT(*) as action_count
FROM actions
WHERE executed_at IS NOT NULL
GROUP BY to_char(executed_at, 'Dy'), EXTRACT(HOUR FROM executed_at)
ORDER BY 
    CASE to_char(executed_at, 'Dy')
        WHEN 'Mon' THEN 1
        WHEN 'Tue' THEN 2
        WHEN 'Wed' THEN 3
        WHEN 'Thu' THEN 4
        WHEN 'Fri' THEN 5
        WHEN 'Sat' THEN 6
        WHEN 'Sun' THEN 7
    END,
    EXTRACT(HOUR FROM executed_at);
