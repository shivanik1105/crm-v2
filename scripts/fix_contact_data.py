"""
Fix contact data - populate churn risk and account values
"""
import asyncio
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
from app.models.contact import Contact
from app.models.email import Email
from app.models.thread import Thread

async def fix_contact_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # Get all contacts
        contacts_stmt = select(Contact)
        result = await session.execute(contacts_stmt)
        contacts = result.scalars().all()
        
        print(f"Updating {len(contacts)} contacts...")
        
        for contact in contacts:
            # Calculate average sentiment from emails
            sentiment_stmt = select(func.avg(Email.sentiment_score)).join(
                Thread, Email.thread_id == Thread.id
            ).where(Thread.sender_email == contact.email)
            
            sentiment_result = await session.execute(sentiment_stmt)
            avg_sentiment = sentiment_result.scalar() or 0.0
            
            # Count negative emails
            negative_stmt = select(func.count(Email.id)).join(
                Thread, Email.thread_id == Thread.id
            ).where(
                Thread.sender_email == contact.email,
                Email.sentiment_score < -0.3
            )
            negative_result = await session.execute(negative_stmt)
            negative_count = negative_result.scalar() or 0
            
            # Calculate churn risk (0-100 scale)
            # High risk if: negative sentiment + multiple complaints
            churn_risk = 0.0
            if avg_sentiment < -0.5:
                churn_risk = min(100, abs(avg_sentiment) * 100 + (negative_count * 15))
            elif avg_sentiment < -0.3:
                churn_risk = min(100, abs(avg_sentiment) * 80 + (negative_count * 10))
            
            # Assign account values based on email patterns
            # VIP customers: karen, bob, alice, eleanor (high-value scenarios)
            account_value = 0.0
            tier = "Starter"
            vip_status = False
            
            if contact.email in ['karen@example.com', 'bob@example.com', 'alice@example.com', 'eleanor@example.com']:
                tier = "Enterprise"
                account_value = 2400.0  # $2,400/year
                vip_status = True
            elif contact.email in ['attacker@evil.com', 'spammer@spam.com']:
                tier = "Blocked"
                account_value = 0.0
                vip_status = False
                churn_risk = 0.0  # Not customers
            elif negative_count > 0:
                tier = "Standard"
                account_value = 149.0  # $149/year
                vip_status = False
            else:
                tier = "Starter"
                account_value = 29.0  # $29/year
                vip_status = False
            
            # Update contact
            contact.churn_risk_score = round(churn_risk, 1)
            contact.account_value = account_value
            contact.tier = tier
            contact.vip_status = vip_status
            
            print(f"  {contact.email}: Churn Risk={churn_risk:.1f}, Value=${account_value}, Tier={tier}, Sentiment={avg_sentiment:.2f}")
        
        await session.commit()
        print("\n✅ Contact data updated successfully!")

if __name__ == "__main__":
    asyncio.run(fix_contact_data())
