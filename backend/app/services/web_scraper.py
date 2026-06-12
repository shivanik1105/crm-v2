import hashlib
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from io import StringIO
import redis.asyncio as redis
from app.config import settings

class WebScraper:
    def __init__(self):
        self.redis_client = None
        self.http_client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.user_agent = "CRM-Intelligence-Bot/1.0"
        self.cache_ttl = 21600  # 6 hours
    
    async def _get_redis(self):
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                pass
        return self.redis_client
    
    async def check_robots_txt(self, url: str) -> bool:
        try:
            parsed = httpx.URL(url)
            robots_url = f"{parsed.scheme}://{parsed.host}/robots.txt"
            
            response = await self.http_client.get(robots_url, headers={"User-Agent": self.user_agent})
            if response.status_code == 200:
                rp = RobotFileParser()
                rp.parse(StringIO(response.text).readlines())
                return rp.can_fetch(self.user_agent, url)
            
            # If robots.txt unreachable, default to allowed (benefit of the doubt)
            return True
        except Exception:
            return True
    
    def _get_cache_key(self, url: str) -> str:
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        return f"web_intel:{url_hash}"
    
    async def _get_cached(self, url: str) -> Optional[Dict[str, Any]]:
        redis_client = await self._get_redis()
        if redis_client is None:
            return None
        
        try:
            cached = await redis_client.get(self._get_cache_key(url))
            if cached:
                import json
                return json.loads(cached)
        except Exception:
            pass
        return None
    
    async def _set_cached(self, url: str, data: Dict[str, Any]):
        redis_client = await self._get_redis()
        if redis_client is None:
            return
        
        try:
            import json
            await redis_client.setex(
                self._get_cache_key(url),
                self.cache_ttl,
                json.dumps(data)
            )
        except Exception:
            pass
    
    async def scrape_g2_trustpilot(self, company_name: str) -> Dict[str, Any]:
        # Simulated scraping for demo purposes
        # In production, this would actually scrape G2/Trustpilot
        return {
            "source": "simulated",
            "company": company_name,
            "g2_rating": 4.2,
            "g2_review_count": 150,
            "trustpilot_rating": 3.8,
            "trustpilot_review_count": 89,
            "common_themes": [
                "Good user interface",
                "Slow customer support response times",
                "Missing advanced reporting features"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        # Check robots.txt
        allowed = await self.check_robots_txt(url)
        if not allowed:
            return {"error": "Disallowed by robots.txt", "url": url}
        
        # Check cache
        cached = await self._get_cached(url)
        if cached:
            cached["cached"] = True
            return cached
        
        try:
            response = await self.http_client.get(
                url,
                headers={"User-Agent": self.user_agent}
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            title = soup.title.string if soup.title else ""
            paragraphs = [p.get_text().strip() for p in soup.find_all('p')[:10]]
            
            result = {
                "url": url,
                "title": title,
                "paragraphs": paragraphs,
                "scraped_at": datetime.utcnow().isoformat(),
                "cached": False
            }
            
            await self._set_cached(url, result)
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "url": url,
                "scraped_at": datetime.utcnow().isoformat()
            }
    
    async def scrape_public_sentiment(self, company_name: str) -> Dict[str, Any]:
        cache_key = f"sentiment:{company_name.lower().replace(' ', '_')}"
        redis_client = await self._get_redis()
        
        if redis_client:
            try:
                import json
                cached = await redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        
        result = await self.scrape_g2_trustpilot(company_name)
        
        if redis_client:
            try:
                import json
                await redis_client.setex(cache_key, self.cache_ttl, json.dumps(result))
            except Exception:
                pass
        
        return result
    
    async def close(self):
        await self.http_client.aclose()
        if self.redis_client:
            await self.redis_client.close()

web_scraper = WebScraper()
