"""Query classification for MF FAQ Assistant."""
import re
from typing import Dict, Any

# Patterns for advice/opinion queries
ADVICE_PATTERNS = [
    r"should i (buy|sell|invest|put)",
    r"is .+ good (to|for) (buy|invest)",
    r"best (fund|scheme|mutual)",
    r"recommend",
    r"which fund (should|to)",
    r"portfolio",
    r"how much should i invest",
    r"worth (buying|investing)",
    r"good investment",
    r"should i (start|stop)",
]

# Patterns for performance queries
PERFORMANCE_PATTERNS = [
    r"return",
    r"performance",
    r"profit",
    r"gain",
    r"yield",
    r"how much (will|would|can) i (make|earn|get)",
    r"what.*return",
    r"how.*perform",
    r"past return",
    r"historical return",
    r"1 year return",
    r"3 year return",
    r"5 year return",
]

# Patterns for greetings
GREETING_PATTERNS = [
    r"^(hi|hello|hey|namaste|good (morning|afternoon|evening))",
    r"^help$",
    r"^what can you do",
]

# Patterns for sentiment (positive/negative)
POSITIVE_SENTIMENT_PATTERNS = [
    # Life events
    r"i am getting married",
    r"i got married",
    r"i had a (baby|twins|triplets|twin)",
    r"i am (pregnant|expecting)",
    r"i (won|achieved|promoted)",
    r"i (passed|cleared|qualified)",
    r"i (bought|purchased) (a |my )?(house|car|home)",
    r"i (got|received) (a )?(job|offer|scholarship)",
    r"i am (celebrating|enjoying)",
    r"i (love|like|enjoy) (it|this|you|football|cricket|movies|music|travel)",
    # Emotions
    r"i am (so |very |really |extremely )?(happy|excited|glad|thrilled|proud|delighted|ecstatic|joyful|elated)",
    r"i feel (great|amazing|wonderful|fantastic|good)",
    r"i am (grateful|thankful|blessed|fortunate)",
    # General positive
    r"congratulations?",
    r"great news",
    r"good news",
    r"thank you",
    r"thanks",
    r"awesome",
    r"amazing",
    r"wonderful",
    r"fantastic",
    r"excellent",
    r"perfect",
    r"brilliant",
    r"outstanding",
    r"superb",
    r"marvelous",
    r"fabulous",
    r"incredible",
    r"extraordinary",
    r"remarkable",
    r"exceptional",
    r"phenomenal",
    r"spectacular",
    r"splendid",
    r"terrific",
    r"tremendous",
    r"stellar",
    r"impressive",
    r"admirable",
    r"commendable",
    r"laudable",
    r"praiseworthy",
    r"deserving",
    r"meritorious",
    r"creditable",
    r"estimable",
    r"respectable",
    r"honorable",
    r"noble",
    r"worthy",
    r"valuable",
    r"precious",
    r"priceless",
    r"invaluable",
    r"irreplaceable",
    r"unique",
    r"rare",
    r"special",
    r"unusual",
]

NEGATIVE_SENTIMENT_PATTERNS = [
    # Life events
    r"my marriage is over",
    r"i (broke up|divorced|separated)",
    r"i (lost|got fired|sacked) (my|from) (job|work)",
    r"i (failed|flunked|bombed) (my|the|exam|test)",
    # Emotions
    r"i am (so |very |really |extremely )?(sad|unhappy|depressed|upset|angry|furious|miserable|heartbroken|devastated|lonely|isolated|abandoned)",
    r"i feel (terrible|awful|horrible|bad|depressed|anxious|worried)",
    "i am (worthless|useless|pathetic|inadequate)",
    r"i (suffer|struggle|grieve|mourn)",
    r"i (regret|repent|rue)",
    r"i am (ashamed|embarrassed|humiliated|mortified)",
    r"i (screwed|messed up|blown|ruined) (it|everything|up)",
    r"i am (doomed|finished|ruined|screwed)",
    r"i (suck|stink|am terrible|am awful)",
    r"i (give up|quit|surrender|throw in the towel)",
    r"i am (defeated|crushed|broken|destroyed)",
    # General negative
    r"bad news",
    r"terrible",
    r"awful",
    r"horrible",
    r"disgusting",
    r"hate",
    r"i (hate|dislike|detest) (it|this|you)",
    r"i (died|passed away)",
    r"i am (sick|ill|dying)",
    r"i am (unemployed|jobless|homeless)",
]

# Patterns for factual queries
FACTUAL_PATTERNS = [
    r"expense ratio",
    r"exit load",
    r"minimum (sip|lumpsum|investment)",
    r"benchmark",
    r"risk",
    r"fund manager",
    r"aum",
    r"nav",
    r"lock.?in",
    r"tax",
    r"stamp duty",
    r"objective",
    r"category",
    r"launch date",
    r"holdings",
    r"how to invest",
    r"how to buy",
    r"how to start",
    r"how to apply",
    r"how to redeem",
    r"how to exit",
    r"how to download",
    r"how to get",
    r"how to check",
    r"how to track",
    r"how to compare",
    r"how to switch",
    r"how to stop",
    r"how to cancel",
    r"how to transfer",
    r"how to withdraw",
    r"how to add",
    r"how to update",
    r"how to change",
    r"how to close",
    r"how to open",
    r"how to link",
    r"how to verify",
    r"how to complete",
    r"how to do",
    r"how to use",
    r"how to find",
    r"how to see",
    r"how to view",
    r"how to access",
    r"how to login",
    r"how to signup",
    r"how to register",
    r"how to kyc",
    r"how to pan",
    r"how to aadhaar",
    r"how to bank",
    r"how to mandate",
    r"how to sip",
    r"how to lumpsum",
    r"how to stp",
    r"how to swp",
    r"how to idcw",
    r"how to reinvest",
    r"kyc",
    r"^elss$",
    r"^sip$",
    r"^aum$",
    r"^nav$",
    r"^tax$",
    r"^exit$",
    r"^load$",
    r"^lock$",
    r"^manager$",
    r"^benchmark$",
    r"^expense$",
    r"^ratio$",
    r"^risk$",
    r"^minimum$",
    r"^investment$",
    r"^what is\b",
    r"^whats\b",
    r"^tell me about\b",
    r"^show\b",
    r"^find\b",
    r"^get\b",
    r"^hdfc\b",
    r"^large cap\b",
    r"^small cap\b",
    r"^flexi\b",
    r"^balanced\b",
    r"^advantage\b",
    r"^tax saver\b",
    r"^mutual fund\b",
    r"^fund\b",
    r"^scheme\b",
]


def classify_query(query: str) -> Dict[str, Any]:
    """
    Classify a user query into a type.
    Returns: {"type": str, "confidence": float}
    """
    query_lower = query.lower().strip()

    # Check advice patterns
    for pattern in ADVICE_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "advice", "confidence": 1.0}

    # Check performance patterns
    for pattern in PERFORMANCE_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "performance", "confidence": 1.0}

    # Check greeting patterns
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "greeting", "confidence": 1.0}

    # Check positive sentiment
    for pattern in POSITIVE_SENTIMENT_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "sentiment_positive", "confidence": 1.0}

    # Check negative sentiment
    for pattern in NEGATIVE_SENTIMENT_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "sentiment_negative", "confidence": 1.0}

    # Check factual patterns
    for pattern in FACTUAL_PATTERNS:
        if re.search(pattern, query_lower):
            return {"type": "factual", "confidence": 0.9}

    # Default: try factual retrieval (might still find relevant chunks)
    return {"type": "factual", "confidence": 0.5}
