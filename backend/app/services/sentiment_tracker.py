import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import redis.asyncio as redis
from app.config import settings
from sqlalchemy import select, desc
from app.database import AsyncSessionLocal
from app.models.email import Email

class SentimentTracker:
    def __init__(self):
        self.redis_client = None
        self.window_size = 10
        self.deterioration_threshold = -0.4
        self.consecutive_threshold = 3
        self._memory_store = defaultdict(list)  # In-memory fallback
    
    async def _get_redis(self):
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            except Exception:
                pass
        return self.redis_client
    
    def _redis_key(self, sender: str) -> str:
        return f"sentiment:{sender.lower()}"
    
    async def record_sentiment(self, sender: str, email_id: str, sentiment_score: float, timestamp: datetime):
        entry = {
            "email_id": email_id,
            "sentiment_score": sentiment_score,
            "timestamp": timestamp.isoformat()
        }
        
        # Always store in memory
        self._memory_store[sender.lower()].append(entry)
        if len(self._memory_store[sender.lower()]) > 50:
            self._memory_store[sender.lower()] = self._memory_store[sender.lower()][-50:]
        
        redis_client = await self._get_redis()
        if redis_client:
            try:
                score = timestamp.timestamp()
                await redis_client.zadd(self._redis_key(sender), {json.dumps(entry): score})
                await redis_client.zremrangebyrank(self._redis_key(sender), 0, -51)
            except Exception:
                pass
    
    async def _get_points_from_db(self, sender: str, days: int = 30) -> List[Dict]:
        """Get sentiment points from database as fallback"""
        try:
            async with AsyncSessionLocal() as db:
                # For demo data, get all emails regardless of date
                # In production, you would use: cutoff = datetime.utcnow() - timedelta(days=days)
                stmt = (
                    select(Email)
                    .where(Email.sender == sender)
                    .where(Email.sentiment_score != None)
                    .order_by(Email.timestamp)
                )
                result = await db.execute(stmt)
                emails = result.scalars().all()
                
                points = []
                for email in emails:
                    points.append({
                        "email_id": str(email.id),
                        "sentiment_score": email.sentiment_score,
                        "timestamp": email.timestamp.isoformat() if email.timestamp else datetime.utcnow().isoformat()
                    })
                return points
        except Exception as e:
            print(f"Error getting points from DB: {e}")
            return []
    
    async def get_sentiment_trend(self, sender: str, days: int = 30) -> Dict[str, Any]:
        # Try memory first
        points = self._memory_store.get(sender.lower(), [])
        
        # Fallback to database
        if not points:
            points = await self._get_points_from_db(sender, days)
        
        if not points:
            return self._empty_trend(sender)
        
        # Sort by timestamp ascending
        points.sort(key=lambda x: x["timestamp"])
        recent = points[-self.window_size:]
        
        scores = [p["sentiment_score"] for p in recent]
        weights = list(range(1, len(scores) + 1))
        weighted_avg = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        
        consecutive_negative = 0
        for score in scores:
            if score < self.deterioration_threshold:
                consecutive_negative += 1
            else:
                consecutive_negative = 0
        
        alert_triggered = consecutive_negative >= self.consecutive_threshold
        
        if len(scores) >= 3:
            first_avg = sum(scores[:3]) / 3
            last_avg = sum(scores[-3:]) / 3
            if last_avg > first_avg + 0.1:
                trend = "improving"
            elif last_avg < first_avg - 0.1:
                trend = "deteriorating"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "sender": sender,
            "points": [
                {
                    "timestamp": datetime.fromisoformat(p["timestamp"]),
                    "sentiment_score": p["sentiment_score"],
                    "email_id": p["email_id"]
                }
                for p in recent
            ],
            "moving_average": round(weighted_avg, 3),
            "trend_direction": trend,
            "alert_triggered": alert_triggered
        }
    
    def _empty_trend(self, sender: str) -> Dict[str, Any]:
        return {
            "sender": sender,
            "points": [],
            "moving_average": 0.0,
            "trend_direction": "stable",
            "alert_triggered": False
        }
    
    async def get_all_trends(self) -> List[Dict[str, Any]]:
        trends = []
        for sender in self._memory_store:
            trends.append(await self.get_sentiment_trend(sender))
        return trends

sentiment_tracker = SentimentTracker()
