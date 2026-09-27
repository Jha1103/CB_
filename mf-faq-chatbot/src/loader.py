"""Load and validate structured facts from JSON."""
import json
from pathlib import Path
from typing import Dict, List, Any


def load_structured_facts(data_dir: Path) -> Dict[str, Any]:
    """Load structured facts from JSON file."""
    facts_path = data_dir / "structured_facts.json"
    if not facts_path.exists():
        raise FileNotFoundError(f"Structured facts not found: {facts_path}")
    with open(facts_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_scheme_by_slug(facts: Dict, slug: str) -> Dict:
    """Get a scheme by its slug."""
    for scheme in facts["schemes"]:
        if scheme["slug"] == slug:
            return scheme
    return None


def get_all_slugs(facts: Dict) -> List[str]:
    """Get all scheme slugs."""
    return [s["slug"] for s in facts["schemes"]]
