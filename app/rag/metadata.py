from pathlib import Path

# filename -> (institution, document_title)
DOCUMENT_REGISTRY: dict[str, tuple[str, str]] = {
    
    # Lombard Odier
    "lombard_odier.txt": (
        "Lombard Odier",
        "Wealth Management and Sustainable Investing Overview",
    ),
    "lombard_odier_sustainability_transition.txt": (
        "Lombard Odier",
        "Sustainability Transition and Long-Term Investing",
    ),
    "lombard_odier_family_governance.txt": (
        "Lombard Odier",
        "Family Governance and Succession",
    ),
    "lombard_odier_private_assets.txt": (
        "Lombard Odier",
        "Private Assets and Alternative Investments",
    ),

    # UBS
    "ubs.txt": (
        "UBS",
        "Private Banking and Wealth Management Overview",
    ),
    "ubs_asset_allocation.txt": (
        "UBS",
        "Strategic Asset Allocation",
    ),
    "ubs_family_office.txt": (
        "UBS",
        "Family Office and Ultra High Net Worth Services",
    ),
    "ubs_digital_wealth_management.txt": (
        "UBS",
        "Digital Wealth Management",
    ),

    # Pictet
    "pictet.txt": (
        "Pictet",
        "Thematic Investing and Asset Management Overview",
    ),
    "pictet_thematic_investing.txt": (
        "Pictet",
        "Thematic Investing Strategies",
    ),
    "pictet_sustainable_finance.txt": (
        "Pictet",
        "Sustainable Finance and Responsible Investing",
    ),
    "pictet_family_wealth.txt": (
        "Pictet",
        "Family Wealth Preservation",
    ),
    "pictet_private_markets.txt": (
        "Pictet",
        "Private Markets and Long-Term Capital",
    ),

    # Julius Baer
    "julius_baer.txt": (
        "Julius Baer",
        "Entrepreneurship and Wealth Planning Overview",
    ),
    "julius_baer_business_owners.txt": (
        "Julius Baer",
        "Services for Business Owners",
    ),
    "julius_baer_responsible_investing.txt": (
        "Julius Baer",
        "Responsible Investing",
    ),
    "julius_baer_digital_banking.txt": (
        "Julius Baer",
        "Digital Banking and Client Experience",
    ),
}


def enrich_document_metadata(file_name: str) -> dict[str, str]:
    name = Path(file_name).name
    institution, title = DOCUMENT_REGISTRY.get(
        name,
        ("Unknown", name.replace("_", " ").replace(".txt", "").title()),
    )
    return {
        "institution": institution,
        "document_title": title,
        "source_file": name,
    }
