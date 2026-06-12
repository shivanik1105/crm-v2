from typing import List

SPAM_KEYWORDS = [
    "nigerian prince", "wire transfer", "seo service", "click here to earn",
    "you've been selected", "free money", "bitcoin investment"
]
SPAM_DOMAINS = ["spam.com", "10minutemail.com", "guerrillamail.com"]
URGENCY_KEYWORDS = [
    "urgent", "p0", "legal", "cease and desist", "ransomware",
    "lawsuit", "breach", "critical", "emergency", "escalate"
]
SECURITY_KEYWORDS = [
    "ransomware", "bitcoin", "btc", "hack", "breach", "suspicious login",
    "unauthorized access", "data leak", "2 btc", "pay or"
]
LEGAL_KEYWORDS = ["legal", "churn", "cancel", "lawsuit", "cease and desist"]

class HeuristicResult:
    def __init__(
        self,
        is_spam: bool = False,
        is_internal: bool = False,
        is_security: bool = False,
        is_urgent: bool = False,
        initial_priority_score: int = 50,
        flags: List[str] = None
    ):
        self.is_spam = is_spam
        self.is_internal = is_internal
        self.is_security = is_security
        self.is_urgent = is_urgent
        self.initial_priority_score = initial_priority_score
        self.flags = flags or []

def calculate_priority_score(body_lower: str, sender_domain: str, flags: List[str]) -> int:
    score = 50
    
    # Security keywords
    for keyword in SECURITY_KEYWORDS:
        if keyword in body_lower:
            score += 30
            if "security" not in flags:
                flags.append("security")
            break
    
    # Urgency keywords
    for keyword in URGENCY_KEYWORDS:
        if keyword in body_lower:
            score += 20
            if "urgency" not in flags:
                flags.append("urgency")
            break
    
    # Legal keywords
    for keyword in LEGAL_KEYWORDS:
        if keyword in body_lower:
            score += 15
            if "legal" not in flags:
                flags.append("legal")
            break
    
    # Spam signals
    spam_detected = False
    for keyword in SPAM_KEYWORDS:
        if keyword in body_lower:
            spam_detected = True
            if "spam" not in flags:
                flags.append("spam")
            break
    
    if sender_domain in SPAM_DOMAINS:
        spam_detected = True
        if "spam_domain" not in flags:
            flags.append("spam_domain")
    
    if spam_detected:
        score -= 40
    
    # Cap between 0 and 100
    return max(0, min(100, score))
