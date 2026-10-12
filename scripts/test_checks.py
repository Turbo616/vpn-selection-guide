"""Regression checks for affiliate visibility and evidence validation."""
import copy
import json
from pathlib import Path
from validate import validate
from render_candidates import render

data = json.loads((Path(__file__).resolve().parents[1] / "data/providers.json").read_text())
item = copy.deepcopy(data[0])
item["affiliate_url"] = "https://example.com/partner?ref=owner"
assert 'href="https://example.com/partner' not in render([item])
item.update(verification_status="official_verified", official_url="https://example.com",
            evidence=["https://example.com/terms"], checked_at="2026-10-12")
assert 'rel="sponsored nofollow"' in render([item])
for change in [{"affiliate_url": "javascript:alert(1)"}, {"evidence": []},
               {"official_url": "https://user:password@example.com"}, {"verification_status": "tested"}]:
    invalid = {**item, **change}
    try:
        validate([invalid])
    except AssertionError:
        pass
    else:
        raise AssertionError(f"Invalid record accepted: {change}")
print("PASS: link visibility, HTTPS, credentials, evidence and test-record gates.")

