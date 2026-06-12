# Compliance FAQ

## HIPAA

### Business Associate Agreement (BAA)
- **Availability:** Enterprise tier only
- **Process:** Request via support, signed via DocuSign within 2 business days
- **Requirements:** Customer must have their own BAA with covered entity
- **Infrastructure:** Dedicated HIPAA-compliant infrastructure with encryption at rest and in transit
- **Audit logs:** 7-year retention, immutable

## GDPR

### Data Processing Agreement (DPA)
- **Availability:** All EU customers regardless of tier
- **Process:** Email privacy@company.com with organization details
- **Signature:** Electronic signature via DocuSign
- **Subprocessors:** List available at trust.company.com/subprocessors

### Article 20 - Data Portability
- **Right:** Customers can request export of their personal data
- **Format:** Machine-readable JSON or CSV
- **Timeline:** 30-day statutory window from receipt of request
- **Delivery:** Secure download link, valid for 7 days
- **Verification:** Identity verification required for requests >10,000 records

### Article 17 - Right to Erasure
- **Process:** Email privacy@company.com with "GDPR Delete Request" in subject
- **Timeline:** 30 days
- **Limitations:** Cannot delete data under legal hold or required for financial records
- **Confirmation:** Written confirmation sent upon completion

## SOC 2 Type II

- **Status:** Certified, audit completed annually
- **Report availability:** Under NDA to Enterprise customers only
- **Request process:** Email security@company.com
- **Controls:** Access control, change management, incident response, business continuity

## Data Residency

### EU Region
- **Availability:** Enterprise tier only
- **Location:** Frankfurt data center (AWS eu-central-1)
- **Setup:** Contact sales for migration
- **Latency:** Add ~20ms latency for US-based users

### US Region
- **Default:** All tiers
- **Location:** US East (AWS us-east-1)

## Eleanor Scenario
Eleanor requires both a HIPAA BAA and SOC 2 Type II report for her 200-seat Enterprise deal. She qualifies for both on Enterprise tier. BAA can be signed within 2 business days via DocuSign. SOC 2 report requires NDA execution first, then report delivery within 3 business days.
