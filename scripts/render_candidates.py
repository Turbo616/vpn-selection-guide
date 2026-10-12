"""Render candidate directory without showing unverified purchase links."""
import html
import json
from pathlib import Path
from validate import validate

ROOT = Path(__file__).resolve().parents[1]

def render(data):
    validate(data)
    rows = ["# VPN 与机场服务商候选清单", "", "[返回选购指南](../README.md)", "",
            "以下 44 个名称来自参考仓库，尚未逐项确认官方身份、运营状态或性能。不是推荐榜单。无资料的条目不展示购买入口。", "",
            "推广披露：启用的推广入口可能为维护者带来佣金。空位置等待维护者提供自己的链接；没有沿用参考仓库的邀请码。", "",
            "| 名称 | 证据状态 | 核查日期 | 入口 |", "| --- | --- | --- | --- |"]
    labels = {"unverified": "待核查", "official_verified": "官方资料已核查", "tested": "已有测试记录"}
    for item in data:
        entry = "推广链接预留，暂未启用"
        if item["affiliate_url"] and item["verification_status"] != "unverified":
            url = html.escape(item["affiliate_url"], quote=True)
            entry = f'<a href="{url}" rel="sponsored nofollow">推广入口（可能产生佣金）</a>'
        rows.append(f'| {item["name"]} | {labels[item["verification_status"]]} | {item["checked_at"] or "—"} | {entry} |')
    rows += ["", "服务商来源记录保存在 [数据文件](../data/providers.json)。名称相似不代表同一经营者，接入链接前必须核实品牌。",
             "", "下一步阅读：[购买检查清单](buying-checklist.md) · [费用与退款](cost-and-refunds.md) · [链接接入说明](affiliate-setup.md)", ""]
    return "\n".join(rows)

if __name__ == "__main__":
    (ROOT / "docs/provider-candidates.md").write_text(render(json.loads((ROOT / "data/providers.json").read_text())))
    print("Candidate directory generated.")

