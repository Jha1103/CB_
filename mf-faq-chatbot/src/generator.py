"""Template-based answer generation for MF FAQ."""
from typing import Dict, Any, Optional

# Educational links
AMFI_URL = "https://www.amfiindia.com"
SEBI_URL = "https://www.sebi.gov.in"
HDFC_FUND_URL = "https://www.hdfcfund.com"

# Refusal messages
ADVICE_REFUSAL = (
    "I can only provide factual information about mutual fund schemes — "
    "I can't give investment advice or recommendations. "
    "For guidance on whether a scheme fits your goals, please consult a "
    "certified financial planner. You can learn more about mutual fund "
    "basics here: {link}"
)

PERFORMANCE_REFUSAL = (
    "I can't compute or compare returns. Please refer to the official "
    "factsheet for performance data: {link}"
)

SENTIMENT_POSITIVE_REFUSAL = (
    "Thank you for sharing that! I'm glad to hear the good news. "
    "However, I can only help with factual questions about HDFC mutual fund schemes. "
    "For example, you can ask me about expense ratio, exit load, minimum SIP, "
    "benchmark, risk level, fund manager, or lock-in period."
)

SENTIMENT_NEGATIVE_REFUSAL = (
    "I'm sorry to hear that. I hope things get better for you. "
    "However, I can only help with factual questions about HDFC mutual fund schemes. "
    "For example, you can ask me about expense ratio, exit load, minimum SIP, "
    "benchmark, risk level, fund manager, or lock-in period."
)


def generate_answer(query_type: str, chunks: list, query: str = "") -> Dict[str, Any]:
    """
    Generate an answer based on query type and retrieved chunks.
    """
    if query_type == "advice":
        return {
            "type": "refusal",
            "answer": ADVICE_REFUSAL.format(link=AMFI_URL),
            "source": AMFI_URL,
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type == "performance":
        # Use the first chunk's source or default to HDFC fund site
        link = chunks[0]["metadata"].get("source_url", HDFC_FUND_URL) if chunks else HDFC_FUND_URL
        return {
            "type": "performance",
            "answer": PERFORMANCE_REFUSAL.format(link=link),
            "source": link,
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type == "greeting":
        return {
            "type": "greeting",
            "answer": (
                "Hello! I'm the MF FAQ Assistant. I can answer factual questions "
                "about HDFC mutual fund schemes — expense ratio, exit load, "
                "minimum SIP, benchmark, risk level, and more. "
                "Facts-only. No investment advice."
            ),
            "source": None,
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type == "sentiment_positive":
        return {
            "type": "sentiment",
            "answer": SENTIMENT_POSITIVE_REFUSAL,
            "source": None,
            "scheme": None,
            "confidence": 1.0,
        }

    if query_type == "sentiment_negative":
        return {
            "type": "sentiment",
            "answer": SENTIMENT_NEGATIVE_REFUSAL,
            "source": None,
            "scheme": None,
            "confidence": 1.0,
        }

    # Handle "how to" queries with a helpful response
    how_to_phrases = ["how to invest", "how to buy", "how to start", "how to apply",
                      "how to redeem", "how to exit", "how to download", "how to get",
                      "how to check", "how to track", "how to compare", "how to switch",
                      "how to stop", "how to cancel", "how to transfer", "how to withdraw",
                      "how to add", "how to update", "how to change", "how to close",
                      "how to open", "how to link", "how to verify", "how to complete",
                      "how to do", "how to use", "how to find", "how to see", "how to view",
                      "how to access", "how to login", "how to signup", "how to register",
                      "how to kyc", "how to pan", "how to aadhaar", "how to bank",
                      "how to mandate", "how to sip", "how to lumpsum", "how to stp",
                      "how to swp", "how to idcw", "how to reinvest"]

    query_lower = query.lower()
    is_how_to = any(phrase in query_lower for phrase in how_to_phrases)

    # Handle KYC queries directly (no chunks needed)
    if "kyc" in query_lower or "know your customer" in query_lower:
        return {
            "type": "factual",
            "answer": (
                "KYC (Know Your Customer) is a one-time verification process required before investing in mutual funds. "
                "You can complete KYC online through your broker/platform by submitting your PAN, Aadhaar, and a selfie. "
                "The process is usually completed within a few hours. "
                "For more details, please visit: https://www.amfiindia.com"
            ),
            "source": "https://www.amfiindia.com",
            "scheme": None,
            "confidence": 1.0,
        }

    # Handle general knowledge queries directly
    general_knowledge = {
        "what is mutual fund": (
            "A mutual fund is an investment vehicle that pools money from multiple investors to invest in stocks, bonds, and other securities. "
            "It is managed by a professional fund manager. "
            "Source: https://www.amfiindia.com"
        ),
        "what is sip": (
            "SIP (Systematic Investment Plan) is a method of investing in mutual funds where you invest a fixed amount at regular intervals (usually monthly). "
            "It helps in disciplined investing and reduces the impact of market volatility. "
            "Source: https://www.amfiindia.com"
        ),
        "what is nav": (
            "NAV (Net Asset Value) is the price at which you can buy or redeem units of a mutual fund scheme. "
            "It is calculated daily by dividing the total net assets of the fund by the number of outstanding units. "
            "Source: https://www.amfiindia.com"
        ),
        "what is expense ratio": (
            "Expense ratio is the annual fee charged by a mutual fund house for managing your investment. "
            "It is expressed as a percentage of the fund's average assets under management (AUM). "
            "Source: https://www.amfiindia.com"
        ),
        "what is exit load": (
            "Exit load is a fee charged by a mutual fund house when you redeem or sell your units before a specified period. "
            "It is usually expressed as a percentage of the redemption amount. "
            "Source: https://www.amfiindia.com"
        ),
        "what is elss": (
            "ELSS (Equity Linked Savings Scheme) is a type of mutual fund that offers tax benefits under Section 80C of the Income Tax Act. "
            "It has a mandatory lock-in period of 3 years. "
            "Source: https://www.amfiindia.com"
        ),
        "what is aum": (
            "AUM (Assets Under Management) represents the total market value of investments managed by a mutual fund scheme. "
            "It indicates the size and popularity of the fund. "
            "Source: https://www.amfiindia.com"
        ),
        "what is benchmark": (
            "A benchmark is an index against which the performance of a mutual fund scheme is measured. "
            "For example, a large-cap fund may use NIFTY 100 as its benchmark. "
            "Source: https://www.amfiindia.com"
        ),
    }

    for key, answer in general_knowledge.items():
        if key in query_lower:
            return {
                "type": "factual",
                "answer": answer,
                "source": "https://www.amfiindia.com",
                "scheme": None,
                "confidence": 1.0,
            }

    if is_how_to and chunks:
        best = chunks[0]
        scheme_name = best["metadata"].get("scheme_name", "")
        source_url = best["metadata"].get("source_url", "")

        # Look up facts from structured facts
        from src.loader import load_structured_facts
        from src.config import DATA_DIR
        facts = load_structured_facts(DATA_DIR)
        min_sip = "N/A"
        min_lumpsum = "N/A"
        exit_load = "N/A"
        for scheme in facts["schemes"]:
            if scheme["name"] == scheme_name:
                min_sip = scheme.get("min_sip", "N/A")
                min_lumpsum = scheme.get("min_lumpsum", "N/A")
                exit_load = scheme.get("exit_load", "N/A")
                break

        # Determine the type of "how to" query
        if "redeem" in query_lower or "exit" in query_lower or "withdraw" in query_lower:
            answer_text = (
                f"To redeem {scheme_name}, you can submit a redemption request online through your broker/platform. "
                f"The exit load for this scheme is: {exit_load}. "
                f"Note: For ELSS funds, there is a 3-year lock-in period and you cannot redeem before that. "
                f"Source: {source_url}"
            )
        elif "download" in query_lower or "statement" in query_lower or "capital gain" in query_lower:
            answer_text = (
                f"You can download your statement or capital gains report from your broker/platform's website or app. "
                f"Log in to your account, go to your mutual fund holdings, and look for the download statement option. "
                f"You can also download the Consolidated Account Statement (CAS) from CAMS or Karvy. "
                f"Source: {source_url}"
            )
        elif "sip" in query_lower or "systematic" in query_lower:
            answer_text = (
                f"You can start a SIP (Systematic Investment Plan) in {scheme_name} through your broker/platform. "
                f"The minimum SIP investment is {min_sip}. "
                f"Log in to your account, search for the scheme, and click on 'Start SIP'. You will need to set the amount, frequency (monthly/quarterly), and a SIP date. "
                f"Source: {source_url}"
            )
        else:
            answer_text = (
                f"To invest in {scheme_name}, you can invest via SIP or lumpsum. "
                f"The minimum SIP investment is {min_sip} and the minimum lumpsum investment is {min_lumpsum}. "
                f"You can invest online through platforms like Groww. "
                f"For detailed step-by-step instructions, please visit: {source_url}"
            )

        return {
            "type": "factual",
            "answer": answer_text,
            "source": source_url,
            "scheme": scheme_name,
            "confidence": best.get("score", 0.0),
        }

    # Factual query
    if not chunks:
        return {
            "type": "not_found",
            "answer": (
                "I don't have that information in my corpus. "
                "I can answer questions about these HDFC schemes: "
                "HDFC Large Cap, HDFC Flexi Cap, HDFC ELSS Tax Saver, "
                "HDFC Small Cap, and HDFC Balanced Advantage. "
                "Try asking about expense ratio, exit load, minimum SIP, "
                "benchmark, risk level, fund manager, NAV, or lock-in period."
            ),
            "source": None,
            "scheme": None,
            "confidence": 0.0,
        }

    # Check if the best chunk is relevant enough
    from src.config import RELEVANCE_THRESHOLD
    best = chunks[0]
    best_score = best.get("score", 0)
    if best_score < RELEVANCE_THRESHOLD:
        return {
            "type": "not_found",
            "answer": (
                "I don't have specific information about that in my corpus. "
                "I can answer questions about these HDFC schemes: "
                "HDFC Large Cap, HDFC Flexi Cap, HDFC ELSS Tax Saver, "
                "HDFC Small Cap, and HDFC Balanced Advantage. "
                "Try asking about expense ratio, exit load, minimum SIP, "
                "benchmark, risk level, fund manager, NAV, or lock-in period."
            ),
            "source": None,
            "scheme": None,
            "confidence": best_score,
        }

    # Use the best chunk
    answer_text = best["text"]
    source_url = best["metadata"].get("source_url", "")
    scheme_name = best["metadata"].get("scheme_name", "")
    category = best["metadata"].get("category_type", "")

    # Build a more helpful answer based on category
    value = best.get("metadata", {}).get("value", "")
    if category == "expense_ratio":
        answer_text = (
            f"{scheme_name} has an expense ratio of {value}. "
            f"This is the annual fee charged by the fund house for managing your investment."
        )
    elif category == "exit_load":
        answer_text = (
            f"For {scheme_name}, the exit load is: {value}. "
            f"This is the fee charged if you redeem units before the specified period."
        )
    elif category == "min_sip":
        answer_text = (
            f"The minimum SIP investment for {scheme_name} is {value}. "
            f"You can start a monthly Systematic Investment Plan with this amount."
        )
    elif category == "min_lumpsum":
        answer_text = (
            f"The minimum lumpsum investment for {scheme_name} is {value}. "
            f"This is the minimum amount you can invest in one go."
        )
    elif category == "benchmark":
        answer_text = (
            f"{scheme_name} uses {value} as its benchmark. "
            f"The fund's performance is measured against this index."
        )
    elif category == "risk_level":
        answer_text = (
            f"{scheme_name} is rated as {value} risk. "
            f"This indicates the level of risk associated with investing in this scheme."
        )
    elif category == "fund_manager":
        answer_text = (
            f"{scheme_name} is managed by {value}. "
            f"The fund manager makes investment decisions for the scheme."
        )
    elif category == "aum":
        answer_text = (
            f"The Assets Under Management (AUM) of {scheme_name} is {value}. "
            f"AUM represents the total market value of investments managed by the fund."
        )
    elif category == "nav":
        answer_text = (
            f"The Net Asset Value (NAV) of {scheme_name} is {value}. "
            f"NAV is the price at which you can buy or redeem units of the scheme."
        )
    elif category == "lock_in":
        answer_text = (
            f"{scheme_name} has a {value} lock-in period. "
            f"You cannot redeem your investment during this period from the date of investment."
        )
    elif category == "tax":
        answer_text = (
            f"Tax implication for {scheme_name}: {value} "
            f"Taxation depends on your holding period and the type of fund."
        )
    elif category == "stamp_duty":
        answer_text = (
            f"Stamp duty on investment for {scheme_name}: {value}. "
            f"This is a government tax applied on the purchase of mutual fund units."
        )
    elif category == "launch_date":
        answer_text = (
            f"{scheme_name} was launched on {value}. "
            f"This is the date when the scheme was first made available to investors."
        )
    elif category == "investment_objective":
        answer_text = (
            f"Investment objective of {scheme_name}: {value} "
            f"This describes what the scheme aims to achieve for investors."
        )

    return {
        "type": "factual",
        "answer": answer_text,
        "source": source_url,
        "scheme": scheme_name,
        "confidence": best.get("score", 0.0),
    }
