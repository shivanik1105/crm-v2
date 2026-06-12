# SLA Policy

## Uptime Commitment

We guarantee 99.9% monthly uptime across all services. This allows approximately 43.8 minutes of downtime per month.

### Uptime Calculation
Uptime is calculated as: (total minutes in month - downtime minutes) / total minutes in month * 100.

## Incident Severity Definitions

### P0 - System Down
- **Definition:** Complete service unavailability or data loss
- **Response Time:** 15 minutes
- **Resolution Target:** 4 hours
- **Communication:** Status page updated within 15 minutes, customer emails within 30 minutes
- **Post-Incident:** Root Cause Analysis (RCA) required within 24 hours
- **Escalation:** On-call Engineer + VP Engineering paged immediately

### P1 - Major Feature Broken
- **Definition:** Core functionality severely degraded but workarounds exist
- **Response Time:** 1 hour
- **Resolution Target:** 8 hours
- **Communication:** Status page updated within 1 hour
- **Escalation:** Engineering Manager + Customer Success Manager notified

### P2 - Minor Issue
- **Definition:** Non-critical features affected, no workaround needed
- **Response Time:** 4 hours
- **Resolution Target:** 24 hours
- **Communication:** Email update to affected customers

### P3 - Cosmetic / Enhancement
- **Definition:** UI issues, feature requests, documentation updates
- **Response Time:** 24 hours
- **Resolution Target:** Next sprint or quarterly release

## Service Credit Formula

If we fail to meet the 99.9% uptime SLA, customers are eligible for service credits:

- **99.0% - 99.9% uptime:** 10% of monthly fee credited
- **98.0% - 99.5% uptime:** 25% of monthly fee credited
- **Below 99.5% uptime:** 50% of monthly fee credited

**Maximum credit:** One month of service fees.

**Credit application:** Applied to next invoice within 30 days of incident resolution.

**Bob Jones Scenario:** Bob Jones experienced a 6-hour outage on his Enterprise plan ($2,400/month). With 6 hours of downtime in a 30-day month (720 hours), uptime was 99.17%. This qualifies for a 50% service credit = $1,200 credited to his next invoice.

## Exclusions
Credits do not apply for downtime caused by:
- Customer's internet connectivity
- Third-party services outside our control
- Scheduled maintenance (with 48-hour notice)
- Force majeure events
