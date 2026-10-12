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
    rows = ["# VPN与机场选购指南：套餐费用、适用人群与使用限制", "",
            "[返回首页](../README.md) · [预算比较](budget-comparison.md) · [年付与流量包](annual-vs-traffic.md)", "",
            "选择VPN或代理订阅，先明确设备、目标地区和月用量，再比较付款周期、流量发放方式与使用限制。下面按品牌整理套餐结构和选择要点，帮助你找到符合实际需求的方案。", "",
            "**价格说明：** 表内为有来源的公开报价，用于比较费用结构，不是实时结算承诺。活动、币种和套餐权益会调整，付款前请核对所选方案的完整金额。原始日期较早的报价不列入当前费用表。", "",
            "**商业披露：** 本项目可能通过已披露的联盟链接获得佣金。套餐结构与使用限制同样适用于有合作和没有合作的品牌。", "",
            "## 品牌目录", "", "| 品牌 | 主要选择要点 |", "| --- | --- |"]
    for p in data:
        rows.append(f'| [{p["name"]}](#{p["id"]}) | 套餐周期、配额与使用限制 |')
    for p in data:
        rows += ["", f'<a id="{p["id"]}"></a>', "", f'## {p["name"]}：套餐与选购要点', "", p["reader_intro"], "", "### 套餐与费用", ""]
        show_prices = p["offers"] and p["id"] not in {"naiyou", "mitu"}
        if show_prices:
            price_label = "官方页面价格" if p["price_status"] == "primary_current" else "公开报价参考"
            rows += [price_label + "。最终金额以所选周期的结算页面为准。", "",
                     "| 套餐档位 | 付款金额与周期 | 配额说明 |", "| --- | --- | --- |"]
            for o in p["offers"]:
                quota = o["quota"]
                if any(t in quota for t in ["待核对", "未在表中列明", "来源未列"]):
                    quota = "按所选套餐的配额说明计算"
                rows.append(f'| {o["name"]} | {money(o)} | {quota} |')
            source_date = p["sources"][0].get("source_date")
            if source_date:
                rows += ["", f"报价资料日期：{source_date}。"]
        elif p["id"] == "wgetcloud":
            rows += ["个人方案分为基础、优质、精品三个等级。季付月流量分别为230G、250G、270G，年付分别为280G、320G、360G。注册后在个人套餐页面选择周期并查看实付金额。"]
        elif p["id"] in {"cloud-vpn", "peiqian", "hongxing"}:
            rows += ["请按具体经营者的产品页面选择套餐。名称相近的服务不使用同一价目表，也不共用账户权益。"]
        else:
            rows += ["付款时按照账户内所选套餐的周期、配额与线路等级计算。旧版价目不作为新的订单报价，长期订阅需查看完整付款金额。"]
        rows += ["", "### 优势与使用限制", ""]
        if show_prices and len(p["offers"]) > 1:
            periods = {o["period"] for o in p["offers"]}
            strength = "提供不同付款周期，便于分别比较短期支出和长期成本。" if len(periods) > 1 else "分档方案便于按用量和预算逐项比较，避免直接购买最高档。"
            rows += ["**方案优势：** " + strength, ""]
        rows += ["**使用限制：** " + p["reader_notice"], "", "### 适用人群", "", p["reader_audience"], "",
                 "### 购买前确认", "", "核对客户端与系统版本、目标地区、同时在线规则、流量重置日和退款条款。按量产品另查到期日期；增值包另查是否需要有效主套餐。", ""]
        if p["id"] == "oixcloud":
            rows += ["付款及充值通常不可退款，个人账号不得共享。", ""]
        elif p["id"] == "shanlian":
            rows += ["官网提供30天退款说明，申请方式与适用渠道按相关条款执行。", ""]
        elif p["id"] == "xsus":
            rows += ["购买须知说明不提供原路返回退款，付款前应确认套餐符合自己的设备与用量。", ""]
        if p["affiliate_url"]:
            rows += ["### 购买入口", "", entry(p), ""]
        rows += ["<details>", "<summary>套餐与使用说明来源</summary>", ""]
        for i, source in enumerate(p["sources"], 1):
            label = "服务商说明" if source["kind"] == "primary" else "公开套餐资料"
            rows.append(f'- [{label} {i}]({source["url"]})')
        rows += ["", "</details>", "", "[返回品牌目录](#品牌目录) · [购买检查清单](buying-checklist.md)", ""]
    return "\n".join(rows)

if __name__ == "__main__":
    (ROOT / "docs/provider-candidates.md").write_text(render(json.loads((ROOT / "data/providers.json").read_text())), encoding="utf-8")
    print("Provider comparison and dossiers generated.")
