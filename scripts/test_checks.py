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
               {"official_url": "https://user:password@example.com"}, {"verification_status": "tested"},
               {"price_status": "primary_current"}, {"price_status": "unknown"}]:
    invalid = {**item, **change}
    try:
        validate([invalid])
    except AssertionError:
        pass
    else:
        raise AssertionError(f"Invalid record accepted: {change}")
invalid = copy.deepcopy(item)
invalid["offers"][0]["source_id"] = "missing"
try:
    validate([invalid])
except AssertionError:
    pass
else:
    raise AssertionError("Accepted a price without evidence")
unknown = copy.deepcopy(next(p for p in data if p["price_status"] == "unknown"))
unknown.update(affiliate_url="https://example.com/partner", verification_status="official_verified",
               official_url="https://example.com")
assert 'href="https://example.com/partner"' not in render([unknown])
directory = render(data)
assert all(f'<a id="{p["id"]}"></a>' in directory for p in data)
assert "参考价，未核现价" in directory and "价格未确认" in directory
print("PASS: affiliate gates, price provenance, missing evidence and complete provider anchors.")

