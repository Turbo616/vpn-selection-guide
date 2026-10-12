"""Validate public data and local Markdown links; no network calls."""
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]

def validate(data):
    ids = set()
    for item in data:
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["id"]), "Invalid ID"
        assert item["id"] not in ids, "Duplicate ID"
        ids.add(item["id"])
        assert item["name"] and not any(c in item["name"] for c in "|\n<>"), "Invalid name"
        assert item["verification_status"] in {"unverified", "official_verified", "tested"}
        for url in [item["affiliate_url"], item["official_url"], *item["evidence"]]:
            if url is not None:
                parsed = urlparse(url)
                assert parsed.scheme == "https" and parsed.hostname, "HTTPS URL required"
                assert not parsed.username and not parsed.password, "Credentials in URL"
        if item["checked_at"] is not None:
            assert date.fromisoformat(item["checked_at"]) <= date.today(), "Future check date"
        if item["verification_status"] != "unverified":
            assert item["official_url"] and item["evidence"] and item["checked_at"], "Evidence required"
        if item["verification_status"] == "tested":
            assert item.get("test_record") and (ROOT / item["test_record"]).is_file(), "Test record required"
        assert item["price_status"] in {"primary_current", "secondary_reference", "unknown"}
        assert item["sources"] and item["summary"] and item["suitable"] and item["not_suitable"]
        sources = {s["id"]: s for s in item["sources"]}
        assert len(sources) == len(item["sources"]), "Duplicate source ID"
        for source in item["sources"]:
            parsed = urlparse(source["url"])
            assert parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password
            assert source["kind"] in {"primary", "reference"}
            assert not (set(parse_qs(parsed.query)) & {"aff", "invite_code", "code", "ref"}), "Referral in evidence URL"
        for offer in item["offers"]:
            assert isinstance(offer["amount"], (int, float)) and not isinstance(offer["amount"], bool) and 0 < offer["amount"] < 100000, "Invalid price"
            assert offer["currency"] in {"CNY", "USD"} and offer["period"] and offer["quota"]
            assert offer["source_id"] in sources, "Price without source"
            if offer.get("quota_source_id"):
                assert offer["quota_source_id"] in sources, "Quota without source"
            if item["price_status"] == "primary_current":
                assert sources[offer["source_id"]]["kind"] == "primary", "Reference called official price"
        if item["price_status"] == "unknown":
            assert not item["offers"], "Unknown price must remain empty"
        else:
            assert item["offers"], "Price status without offers"

def main():
    data = json.loads((ROOT / "data/providers.json").read_text())
    validate(data)
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if urlparse(target).scheme:
                continue
            file_part, _, anchor = target.partition("#")
            destination = path.parent / file_part if file_part else path
            assert destination.exists(), f"Missing link: {path}: {target}"
            if anchor and destination.suffix == ".md":
                content = destination.read_text()
                explicit = re.findall(r'<a id="([^"]+)"', content)
                headings = [re.sub(r"[^\w\s-]", "", h.lower()).replace(" ", "-")
                            for h in re.findall(r"^#+ (.+)$", content, re.M)]
                assert anchor in explicit + headings, f"Missing anchor: {path}: {target}"
    assert len(data) == 44, "Provider coverage changed"
    print(f"PASS: {len(data)} providers, evidence, price provenance and local Markdown links.")

if __name__ == "__main__":
    main()

