-- Fix Contact Data: Populate churn_risk_score and account_value
-- Run this with: docker compose exec postgres psql -U crm -d crm_db -f /app/fix_contacts.sql

-- Update Karen (angry, VIP, high churn risk)
UPDATE contacts 
SET 
  churn_risk_score = 85.0,
  account_value = 2400.0,
  tier = 'Enterprise',
  vip_status = true
WHERE email = 'karen@example.com';

-- Update Bob (frustrated, VIP, moderate-high churn risk)
UPDATE contacts 
SET 
  churn_risk_score = 65.0,
  account_value = 2400.0,
  tier = 'Enterprise',
  vip_status = true
WHERE email = 'bob@example.com';

-- Update Alice (satisfied, VIP, low churn risk)
UPDATE contacts 
SET 
  churn_risk_score = 25.0,
  account_value = 2400.0,
  tier = 'Enterprise',
  vip_status = true
WHERE email = 'alice@example.com';

-- Update Eleanor (neutral, VIP, low-moderate churn risk)
UPDATE contacts 
SET 
  churn_risk_score = 30.0,
  account_value = 2400.0,
  tier = 'Enterprise',
  vip_status = true
WHERE email = 'eleanor@example.com';

-- Update Charlie (satisfied, Standard, low churn risk)
UPDATE contacts 
SET 
  churn_risk_score = 20.0,
  account_value = 149.0,
  tier = 'Standard',
  vip_status = false
WHERE email = 'charlie@example.com';

-- Update Dan (neutral, Standard, moderate churn risk)
UPDATE contacts 
SET 
  churn_risk_score = 45.0,
  account_value = 149.0,
  tier = 'Standard',
  vip_status = false
WHERE email = 'dan@example.com';

-- Update Frank (frustrated, Standard, moderate churn risk)
UPDATE contacts 
SET 
  churn_risk_score = 55.0,
  account_value = 149.0,
  tier = 'Standard',
  vip_status = false
WHERE email = 'frank@example.com';

-- Update Grace (satisfied, Starter, low churn risk)
UPDATE contacts 
SET 
  churn_risk_score = 15.0,
  account_value = 29.0,
  tier = 'Starter',
  vip_status = false
WHERE email = 'grace@example.com';

-- Show updated contacts
SELECT email, churn_risk_score, account_value, tier, vip_status 
FROM contacts 
ORDER BY churn_risk_score DESC;
