"""
Update contacts with realistic data based on email scenarios
"""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.contact import Contact

CONTACT_DATA = {
    # Karen - churn threat, Standard tier, public review threat
    "karen@example.com": {
        "name": "Karen Williams",
        "tier": "Standard",
        "account_value": 149.0,  # $149/mo
        "vip_status": False,
        "churn_risk_score": 85.0,  # High churn risk
    },
    # Bob - Enterprise, P0 outage, legal escalation
    "bob@example.com": {
        "name": "Bob Johnson",
        "tier": "Enterprise",
        "account_value": 2400.0,  # $2,400/mo
        "vip_status": True,
        "churn_risk_score": 75.0,  # High due to outage
    },
    # Alice - Non-profit, pricing negotiation
    "alice@example.com": {
        "name": "Alice Smith",
        "tier": "Standard",
        "account_value": 104.3,  # $149 * 0.7 (30% non-profit discount)
        "vip_status": False,
        "churn_risk_score": 15.0,  # Low risk, happy customer
    },
    # Eleanor - Enterprise HIPAA compliance
    "eleanor@example.com": {
        "name": "Eleanor Chen",
        "tier": "Enterprise",
        "account_value": 3200.0,  # 200 seats * $16/seat
        "vip_status": True,
        "churn_risk_score": 20.0,  # Low risk, in compliance review
    },
    # Marcus - GDPR request
    "marcus.del@fintech-startup.co": {
        "name": "Marcus Delgado",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 30.0,
    },
    # Attacker - blocked
    "attacker@evil.com": {
        "name": "Unknown Attacker",
        "tier": "Starter",
        "account_value": 0.0,
        "vip_status": False,
        "churn_risk_score": 0.0,
    },
    # Spammer - blocked
    "spammer@spam.com": {
        "name": "Spam Bot",
        "tier": "Starter",
        "account_value": 0.0,
        "vip_status": False,
        "churn_risk_score": 0.0,
    },
    # Additional contacts with realistic values
    "charlie@example.com": {
        "name": "Charlie Brown",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 25.0,
    },
    "diana@example.com": {
        "name": "Diana Prince",
        "tier": "Enterprise",
        "account_value": 1800.0,
        "vip_status": True,
        "churn_risk_score": 10.0,
    },
    "frank@example.com": {
        "name": "Frank Miller",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 45.0,  # Billing dispute
    },
    "grace@example.com": {
        "name": "Grace Lee",
        "tier": "Starter",
        "account_value": 49.0,
        "vip_status": False,
        "churn_risk_score": 20.0,
    },
    "henry@example.com": {
        "name": "Henry Wilson",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 35.0,
    },
    "leo@example.com": {
        "name": "Leo Martinez",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 55.0,  # Slow performance issues
    },
    "olivia@example.com": {
        "name": "Olivia Taylor",
        "tier": "Enterprise",
        "account_value": 2100.0,
        "vip_status": True,
        "churn_risk_score": 40.0,  # Mobile app crash
    },
    "peter@example.com": {
        "name": "Peter Parker",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 30.0,
    },
    "sam@example.com": {
        "name": "Sam Wilson",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 50.0,  # Webhook issues
    },
    "tara@example.com": {
        "name": "Tara Singh",
        "tier": "Enterprise",
        "account_value": 2800.0,
        "vip_status": True,
        "churn_risk_score": 15.0,
    },
    "umar@example.com": {
        "name": "Umar Hassan",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 25.0,
    },
    "anna@example.com": {
        "name": "Anna Kowalski",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 60.0,  # 2FA issues
    },
    "gina@example.com": {
        "name": "Gina Rodriguez",
        "tier": "Standard",
        "account_value": 149.0,
        "vip_status": False,
        "churn_risk_score": 45.0,  # Email threading bug
    },
}


async def update_contacts():
    async with AsyncSessionLocal() as db:
        # Get all contacts
        result = await db.execute(select(Contact))
        contacts = result.scalars().all()
        
        updated = 0
        for contact in contacts:
            if contact.email in CONTACT_DATA:
                data = CONTACT_DATA[contact.email]
                contact.name = data["name"]
                contact.tier = data["tier"]
                contact.account_value = data["account_value"]
                contact.vip_status = data["vip_status"]
                contact.churn_risk_score = data["churn_risk_score"]
                updated += 1
                print(f"Updated {contact.email}: {data['tier']} tier, ${data['account_value']}/mo, churn risk {data['churn_risk_score']}")
        
        await db.commit()
        print(f"\nUpdated {updated} contacts")


if __name__ == "__main__":
    asyncio.run(update_contacts())
