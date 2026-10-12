"""Validate public data and local Markdown links; no network calls."""
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

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

def main():
    data = json.loads((ROOT / "data/providers.json").read_text())
    validate(data)
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if urlparse(target).scheme or target.startswith("#"):
                continue
            assert (path.parent / target.split("#")[0]).exists(), f"Missing link: {path}: {target}"
    print(f"PASS: {len(data)} providers, schema and local Markdown links.")

if __name__ == "__main__":
    main()

