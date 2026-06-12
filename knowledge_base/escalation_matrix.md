# Escalation Matrix

## Escalation Criteria and Routes

### Legal Threats
- **Triggers:** Cease and desist, lawsuit mentions, legal action threats, defamation claims
- **Route:** Legal Team (legal@company.com)
- **Response SLA:** 2 hours
- **Auto-actions:** Flag email, create legal review ticket, suspend auto-reply
- **Stakeholders:** General Counsel, VP Legal, CEO if public

### Security Incidents
- **Triggers:** Ransomware, breach reports, unauthorized access, data leak reports
- **Route:** Security Team (security@company.com) + CTO
- **Response SLA:** Immediate
- **Auto-actions:** Isolate affected systems, initiate incident response protocol
- **Stakeholders:** CISO, CTO, VP Engineering, Legal

### P0 Outages
- **Triggers:** Complete system unavailability
- **Route:** On-call Engineer + VP Engineering
- **Response SLA:** 15-minute page
- **Auto-actions:** Status page update, customer communication, war room activation
- **Stakeholders:** All Engineering leadership, Customer Success leadership

### GDPR Requests
- **Triggers:** Data portability requests, erasure requests, any "Article 20" mention
- **Route:** Data Protection Officer (privacy@company.com)
- **Response SLA:** Acknowledge within 24 hours, resolve within 30 days
- **Auto-actions:** Create compliance ticket, start 30-day countdown
- **Stakeholders:** DPO, Legal, Engineering (for data export)

### VIP Churn Threats
- **Triggers:** Account value >$1,000/month threatening cancellation
- **Route:** Account Executive + VP Customer Success
- **Response SLA:** 4 hours
- **Auto-actions:** Create retention opportunity, alert CSM, schedule executive call
- **Stakeholders:** AE, VP CS, CFO if discount >$5,000

### PR / Reputation Threats
- **Triggers:** Public review threats, social media complaints, journalist inquiries
- **Route:** Marketing + CEO if public review already threatened or published
- **Response SLA:** 2 hours for public threats, immediate for published reviews
- **Auto-actions:** Monitor social channels, prepare holding statement
- **Stakeholders:** CMO, CEO, Legal, Customer Success

### Low Confidence Classification
- **Triggers:** AI confidence score <0.70
- **Route:** Human review queue
- **Response SLA:** Next business day
- **Auto-actions:** Do NOT auto-reply, flag for senior agent review
- **Stakeholders:** Senior Support Agents, Team Lead

## Escalation Playbook

1. **Never auto-reply** to emails in Legal, Security, or GDPR categories
2. **Always create a ticket** for tracking and audit purposes
3. **Document reasoning** in the escalation brief for handoff
4. **Set calendar reminders** for SLA deadlines (especially GDPR 30-day window)
5. **Notify stakeholders** via Slack/email within SLA timeframe
