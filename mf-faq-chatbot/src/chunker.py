"""Fact-based semantic chunking for MF FAQ."""
from typing import Dict, List, Any


def chunk_scheme_facts(facts: Dict) -> List[Dict[str, Any]]:
    """
    Convert structured facts into atomic chunks.
    Each chunk = one fact about one scheme.
    """
    chunks = []

    for scheme in facts["schemes"]:
        slug = scheme["slug"]
        name = scheme["name"]
        source_url = scheme["source_url"]

        # Expense ratio
        chunks.append(_make_chunk(
            id=f"{slug}_expense_ratio",
            scheme=name, slug=slug, category="expense_ratio",
            text=f"The expense ratio of {name} is {scheme['expense_ratio']}.",
            value=scheme["expense_ratio"],
            source_url=source_url
        ))

        # Exit load
        chunks.append(_make_chunk(
            id=f"{slug}_exit_load",
            scheme=name, slug=slug, category="exit_load",
            text=f"Exit load of {name}: {scheme['exit_load']}.",
            value=scheme["exit_load"],
            source_url=source_url
        ))

        # Min SIP
        chunks.append(_make_chunk(
            id=f"{slug}_min_sip",
            scheme=name, slug=slug, category="min_sip",
            text=f"The minimum SIP investment for {name} is {scheme['min_sip']}.",
            value=scheme["min_sip"],
            source_url=source_url
        ))

        # Min lumpsum
        chunks.append(_make_chunk(
            id=f"{slug}_min_lumpsum",
            scheme=name, slug=slug, category="min_lumpsum",
            text=f"The minimum lumpsum investment for {name} is {scheme['min_lumpsum']}.",
            value=scheme["min_lumpsum"],
            source_url=source_url
        ))

        # Benchmark
        chunks.append(_make_chunk(
            id=f"{slug}_benchmark",
            scheme=name, slug=slug, category="benchmark",
            text=f"The benchmark of {name} is {scheme['benchmark']}.",
            value=scheme["benchmark"],
            source_url=source_url
        ))

        # Risk level
        chunks.append(_make_chunk(
            id=f"{slug}_risk_level",
            scheme=name, slug=slug, category="risk_level",
            text=f"{name} is rated {scheme['risk_level']} risk.",
            value=scheme["risk_level"],
            source_url=source_url
        ))

        # Fund managers
        managers = ", ".join([m["name"] for m in scheme["fund_managers"]])
        chunks.append(_make_chunk(
            id=f"{slug}_fund_manager",
            scheme=name, slug=slug, category="fund_manager",
            text=f"{name} is managed by {managers}.",
            value=managers,
            source_url=source_url
        ))

        # AUM
        chunks.append(_make_chunk(
            id=f"{slug}_aum",
            scheme=name, slug=slug, category="aum",
            text=f"The AUM of {name} is {scheme['aum']}.",
            value=scheme["aum"],
            source_url=source_url
        ))

        # NAV
        chunks.append(_make_chunk(
            id=f"{slug}_nav",
            scheme=name, slug=slug, category="nav",
            text=f"The NAV of {name} as of {scheme['nav_date']} is {scheme['nav']}.",
            value=scheme["nav"],
            source_url=source_url
        ))

        # Launch date
        chunks.append(_make_chunk(
            id=f"{slug}_launch_date",
            scheme=name, slug=slug, category="launch_date",
            text=f"{name} was launched on {scheme['launch_date']}.",
            value=scheme["launch_date"],
            source_url=source_url
        ))

        # Investment objective
        chunks.append(_make_chunk(
            id=f"{slug}_objective",
            scheme=name, slug=slug, category="investment_objective",
            text=f"{name} seeks to {scheme['investment_objective']}",
            value=scheme["investment_objective"],
            source_url=source_url
        ))

        # Lock-in (ELSS only)
        if scheme.get("lock_in"):
            chunks.append(_make_chunk(
                id=f"{slug}_lock_in",
                scheme=name, slug=slug, category="lock_in",
                text=f"{name} has a {scheme['lock_in']} lock-in period.",
                value=scheme["lock_in"],
                source_url=source_url
            ))

        # Tax
        chunks.append(_make_chunk(
            id=f"{slug}_tax",
            scheme=name, slug=slug, category="tax",
            text=f"Tax implication for {name}: {scheme['tax_implication']}",
            value=scheme["tax_implication"],
            source_url=source_url
        ))

        # Stamp duty
        chunks.append(_make_chunk(
            id=f"{slug}_stamp_duty",
            scheme=name, slug=slug, category="stamp_duty",
            text=f"Stamp duty on investment for {name}: {scheme['stamp_duty']}.",
            value=scheme["stamp_duty"],
            source_url=source_url
        ))

        # Top holdings
        holdings = scheme.get("top_holdings", [])
        if holdings:
            holdings_text = ", ".join([f"{h['name']} ({h['pct']})" for h in holdings])
            chunks.append(_make_chunk(
                id=f"{slug}_holdings",
                scheme=name, slug=slug, category="holdings",
                text=f"The top holdings of {name} are: {holdings_text}.",
                value=holdings_text,
                source_url=source_url
            ))

    # General knowledge chunks (not scheme-specific)
    general_knowledge = [
        {
            "id": "general_what_is_mutual_fund",
            "scheme": "General",
            "slug": "general",
            "category": "general_knowledge",
            "text": "A mutual fund is an investment vehicle that pools money from multiple investors to invest in stocks, bonds, and other securities. It is managed by a professional fund manager.",
            "value": "A mutual fund is an investment vehicle that pools money from multiple investors to invest in stocks, bonds, and other securities.",
            "source_url": "https://www.amfiindia.com",
            "metadata": {
                "amc": "General",
                "scheme_name": "General",
                "category_type": "general_knowledge",
                "source_url": "https://www.amfiindia.com",
                "value": "A mutual fund is an investment vehicle that pools money from multiple investors to invest in stocks, bonds, and other securities.",
            }
        },
        {
            "id": "general_what_is_sip",
            "scheme": "General",
            "slug": "general",
            "category": "general_knowledge",
            "text": "SIP (Systematic Investment Plan) is a method of investing in mutual funds where you invest a fixed amount at regular intervals (usually monthly). It helps in disciplined investing and reduces the impact of market volatility.",
            "value": "SIP (Systematic Investment Plan) is a method of investing in mutual funds where you invest a fixed amount at regular intervals (usually monthly).",
            "source_url": "https://www.amfiindia.com",
            "metadata": {
                "amc": "General",
                "scheme_name": "General",
                "category_type": "general_knowledge",
                "source_url": "https://www.amfiindia.com",
                "value": "SIP (Systematic Investment Plan) is a method of investing in mutual funds where you invest a fixed amount at regular intervals (usually monthly).",
            }
        },
        {
            "id": "general_what_is_nav",
            "scheme": "General",
            "slug": "general",
            "category": "general_knowledge",
            "text": "NAV (Net Asset Value) is the price at which you can buy or redeem units of a mutual fund scheme. It is calculated daily by dividing the total net assets of the fund by the number of outstanding units.",
            "value": "NAV (Net Asset Value) is the price at which you can buy or redeem units of a mutual fund scheme.",
            "source_url": "https://www.amfiindia.com",
            "metadata": {
                "amc": "General",
                "scheme_name": "General",
                "category_type": "general_knowledge",
                "source_url": "https://www.amfiindia.com",
                "value": "NAV (Net Asset Value) is the price at which you can buy or redeem units of a mutual fund scheme.",
            }
        },
        {
            "id": "general_what_is_expense_ratio",
            "scheme": "General",
            "slug": "general",
            "category": "general_knowledge",
            "text": "Expense ratio is the annual fee charged by a mutual fund house for managing your investment. It is expressed as a percentage of the fund's average assets under management (AUM) and includes management fees, administrative costs, and other operational expenses.",
            "value": "Expense ratio is the annual fee charged by a mutual fund house for managing your investment.",
            "source_url": "https://www.amfiindia.com",
            "metadata": {
                "amc": "General",
                "scheme_name": "General",
                "category_type": "general_knowledge",
                "source_url": "https://www.amfiindia.com",
                "value": "Expense ratio is the annual fee charged by a mutual fund house for managing your investment.",
            }
        },
        {
            "id": "general_what_is_exit_load",
            "scheme": "General",
            "slug": "general",
            "category": "general_knowledge",
            "text": "Exit load is a fee charged by a mutual fund house when you redeem or sell your units before a specified period. It is usually expressed as a percentage of the redemption amount and is used to discourage short-term redemptions.",
            "value": "Exit load is a fee charged by a mutual fund house when you redeem or sell your units before a specified period.",
            "source_url": "https://www.amfiindia.com",
            "metadata": {
                "amc": "General",
                "scheme_name": "General",
                "category_type": "general_knowledge",
                "source_url": "https://www.amfiindia.com",
                "value": "Exit load is a fee charged by a mutual fund house when you redeem or sell your units before a specified period.",
            }
        },
        {
            "id": "general_what_is_elss",
            "scheme": "General",
            "slug": "general",
            "category": "general_knowledge",
            "text": "ELSS (Equity Linked Savings Scheme) is a type of mutual fund that offers tax benefits under Section 80C of the Income Tax Act. It has a mandatory lock-in period of 3 years and invests primarily in equity and equity-related instruments.",
            "value": "ELSS (Equity Linked Savings Scheme) is a type of mutual fund that offers tax benefits under Section 80C of the Income Tax Act.",
            "source_url": "https://www.amfiindia.com",
            "metadata": {
                "amc": "General",
                "scheme_name": "General",
                "category_type": "general_knowledge",
                "source_url": "https://www.amfiindia.com",
                "value": "ELSS (Equity Linked Savings Scheme) is a type of mutual fund that offers tax benefits under Section 80C of the Income Tax Act.",
            }
        },
        {
            "id": "general_what_is_aum",
            "scheme": "General",
            "slug": "general",
            "category": "general_knowledge",
            "text": "AUM (Assets Under Management) represents the total market value of investments managed by a mutual fund scheme. It indicates the size and popularity of the fund among investors.",
            "value": "AUM (Assets Under Management) represents the total market value of investments managed by a mutual fund scheme.",
            "source_url": "https://www.amfiindia.com",
            "metadata": {
                "amc": "General",
                "scheme_name": "General",
                "category_type": "general_knowledge",
                "source_url": "https://www.amfiindia.com",
                "value": "AUM (Assets Under Management) represents the total market value of investments managed by a mutual fund scheme.",
            }
        },
        {
            "id": "general_what_is_benchmark",
            "scheme": "General",
            "slug": "general",
            "category": "general_knowledge",
            "text": "A benchmark is an index against which the performance of a mutual fund scheme is measured. For example, a large-cap fund may use NIFTY 100 as its benchmark. The fund aims to outperform its benchmark over the long term.",
            "value": "A benchmark is an index against which the performance of a mutual fund scheme is measured.",
            "source_url": "https://www.amfiindia.com",
            "metadata": {
                "amc": "General",
                "scheme_name": "General",
                "category_type": "general_knowledge",
                "source_url": "https://www.amfiindia.com",
                "value": "A benchmark is an index against which the performance of a mutual fund scheme is measured.",
            }
        },
    ]

    chunks.extend(general_knowledge)
    return chunks


def _make_chunk(id, scheme, slug, category, text, value, source_url):
    return {
        "id": id,
        "scheme": scheme,
        "slug": slug,
        "category": category,
        "text": text,
        "value": value,
        "source_url": source_url,
        "metadata": {
            "amc": "HDFC Mutual Fund",
            "scheme_name": scheme,
            "category_type": category,
            "source_url": source_url,
            "value": value,
        }
    }
