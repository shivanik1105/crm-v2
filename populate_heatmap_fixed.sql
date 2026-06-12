-- Simplified version without executed_at column
DO $$
DECLARE
    email_record RECORD;
    response_time INTERVAL;
BEGIN
    FOR email_record IN 
        SELECT id, timestamp, sender 
        FROM emails 
        WHERE status = 'Replied' 
        AND timestamp IS NOT NULL
        LIMIT 100
    LOOP
        -- Random response time between 1 minute and 60 minutes
        response_time = (random() * 59 + 1) * INTERVAL '1 minute';
        
        INSERT INTO actions (
            id,
            email_id,
            action_type,
            reasoning,
            status
        ) VALUES (
            gen_random_uuid(),
            email_record.id,
            'auto_reply',
            '{"decision": "auto_reply", "confidence": 0.9}',
            'completed'
        ) ON CONFLICT DO NOTHING;
    END LOOP;
END $$;
