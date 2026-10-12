"""Generate the comparison and provider dossiers."""
import html
import json
from collections import Counter
from pathlib import Path
from validate import validate

ROOT = Path(__file__).resolve().parents[1]
LABELS = {"primary_current": "官方公开价", "secondary_reference": "参考价，未核现价", "unknown": "价格未确认"}

def money(offer):
    symbol = {"CNY": "¥", "USD": "US$"}[offer["currency"]]
    return f'{symbol}{offer["amount"]:g} / {offer["period"]}'

def entry(item):
    if item["affiliate_url"] and item["verification_status"] != "unverified" and item["price_status"] != "unknown":
        url = html.escape(item["affiliate_url"], quote=True)
        return f'<a href="{url}" rel="sponsored nofollow">推广入口（可能产生佣金）</a>'
    return "推广链接预留，暂未启用"

def render(data):
    validate(data)
    counts = Counter(p["price_status"] for p in data)
    rows = [f'# {len(data)} 家 VPN 与机场套餐价格对比：资料、优缺点与适用人群', "",
            "[返回首页](../README.md) · [预算怎么比较](budget-comparison.md) · [品牌与官网辨别](brand-identity.md)", "",
            "本轮资料检索：2026-10-12（Asia/Shanghai）。维护者：[Turbo616](https://github.com/Turbo616)。", "",
            f'公开官网可读价格 {counts["primary_current"]} 家；仅取得第三方或历史价格 {counts["secondary_reference"]} 家；价格无法可靠确认 {counts["unknown"]} 家。**这不是44家现价已全部核实，也不是实测排名。**', "",
            "推广披露：后续接入维护者联盟链接后，购买可能产生佣金。当前全部留空，没有复制第三方邀请码。", "",
            "参考价用于了解套餐结构与预算线索，不能代替本家结算价。检索日期不是原始报价日期。优缺点和适用人群是依据已列资料作出的选购分析，未进行节点测速、付款或退款测试。", "",
            "## 快速比较", "", "价格栏只展示一项样例，不表示最低价或推荐购买。不同币种、季度、年度和加购项目不能直接比较。", "",
            "| 服务商 | 价格样例 | 证据 | 资料 |", "| --- | --- | --- | --- |"]
    for p in data:
        price = money(p["offers"][0]) if p["offers"] else "未确认"
        rows.append(f'| [{p["name"]}](#{p["id"]}) | {price} | {LABELS[p["price_status"]]} | [套餐与限制](#{p["id"]}) |')
    rows += ["", "## 如何阅读品牌档案", "",
             "官方公开价表示本次直接读取服务商页面，不证明性能、匿名性或长期运营。参考价表示来源是第三方资料；较旧、不一致和缺失项目均注明。没有价格时保留空缺，不拼接同名服务报价。", ""]
    for p in data:
        rows += [f'<a id="{p["id"]}"></a>', "", f'## {p["name"]}：套餐、优缺点与适用人群', "",
                 p["summary"], "", f'**价格证据：{LABELS[p["price_status"]]}。** 资料检索于 {p["researched_at"]}；原始报价日期：{p["source_date_note"]}。', ""]
        if p["offers"]:
            rows += ["### 套餐与价格", "", "以下为来源中的代表档位，不是完整在售商店或已验证优惠。", "",
                     "| 代表档位 | 实付／周期 | 流量口径 |", "| --- | --- | --- |"]
            rows += [f'| {o["name"]} | {money(o)} | {o["quota"]} |' for o in p["offers"]]
        else:
            rows += ["### 套餐与价格", "", "本次没有可靠的可读价格。请先确认品牌对应及官方当期价目，暂不提供付费入口。"]
        rows += ["", "### 优点与限制", "", "**可供比较的优势（资料分析）：** " + " ".join(p["advantages"]), "",
                 "**不足与待确认事项：** " + " ".join(p["limitations"]), "", "### 适合与不适合的人群", "",
                 "**可考虑的人群：** " + p["suitable"], "", "**不建议直接购买的人群：** " + p["not_suitable"], "",
                 "### 付款、客户端与续费提醒", "", p["purchase_note"], "", "**退款：** " + p["refund_note"], "",
                 "**推广入口：** " + entry(p), "", "### 资料来源", ""]
        for i, s in enumerate(p["sources"], 1):
            label = "本家公开页面／公告线索" if s["kind"] == "primary" else "第三方参考／历史资料"
            rows.append(f'- [{label} {i}]({s["url"]})（读取日期：{s["checked_at"]}）')
        rows += ["", "[回到比较表](#快速比较) · [购买前检查](buying-checklist.md)", ""]
    return "\n".join(rows)

if __name__ == "__main__":
    (ROOT / "docs/provider-candidates.md").write_text(render(json.loads((ROOT / "data/providers.json").read_text())), encoding="utf-8")
    print("Provider comparison and dossiers generated.")
