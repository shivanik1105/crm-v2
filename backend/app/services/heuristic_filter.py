from typing import List
from app.schemas.email import EmailIngest
from app.utils.priority_scorer import calculate_priority_score

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

def heuristic_filter(email: EmailIngest) -> HeuristicResult:
    body_lower = email.body.lower()
    sender_domain = email.sender.split("@")[-1].lower() if "@" in email.sender else ""
    flags: List[str] = []
    
    is_spam = False
    is_security = False
    is_urgent = False
    is_internal = False
    
    # Check spam keywords
    spam_keywords = [
        "nigerian prince", "wire transfer", "seo service", "click here to earn",
        "you've been selected", "free money", "bitcoin investment"
    ]
    spam_domains = ["spam.com", "10minutemail.com", "guerrillamail.com"]
    
    for keyword in spam_keywords:
        if keyword in body_lower:
            is_spam = True
            flags.append("spam_keyword")
            break
    
    if sender_domain in spam_domains:
        is_spam = True
        flags.append("spam_domain")
    
    # Check security keywords
    security_keywords = [
        "ransomware", "bitcoin", "btc", "hack", "breach", "suspicious login",
        "unauthorized access", "data leak", "2 btc", "pay or"
    ]
    
    for keyword in security_keywords:
        if keyword in body_lower:
            is_security = True
            flags.append("security_keyword")
            break
    
    # Check urgency keywords
    urgency_keywords = [
        "urgent", "p0", "legal", "cease and desist", "ransomware",
        "lawsuit", "breach", "critical", "emergency", "escalate"
    ]
    
    for keyword in urgency_keywords:
        if keyword in body_lower:
            is_urgent = True
            flags.append("urgency_keyword")
            break
    
    # Check internal domains
    internal_domains = ["internal.com", "mycompany.com"]
    if sender_domain in internal_domains:
        is_internal = True
        flags.append("internal_domain")
    
    # Calculate priority score
    priority_score = calculate_priority_score(body_lower, sender_domain, flags)
    
    return HeuristicResult(
        is_spam=is_spam,
        is_internal=is_internal,
        is_security=is_security,
        is_urgent=is_urgent,
        initial_priority_score=priority_score,
        flags=flags
    )
