# 如何接入自己的 VPN 联盟链接

[返回选购指南](../README.md)

当前 44 个服务商均预留了链接字段，没有放入原作者链接。维护者收到“服务商名称 + 个人推广链接”后逐项匹配；没有覆盖的品牌保持空值。

## 数据位置

编辑 [data/providers.json](../data/providers.json)：

- affiliate_url：你的公开联盟推广链接；未提供时为 null。
- official_url：已核实的官方入口；未核实为 null。
- verification_status：unverified、official_verified 或 tested。
- evidence：公开来源地址列表，不放私人订单或订阅密钥。
- checked_at：实际资料核查日期，格式 YYYY-MM-DD。

提供联盟链接本身不证明产品可靠。完成官方资料核查和佣金披露后，才将状态改为 official_verified；tested 还需要测试记录。链接必须使用 HTTPS，不能把账号、密码或私人订阅地址当成推广链接。

## 生成与验证

在仓库根目录执行：

```sh
python3 scripts/validate.py
python3 scripts/render_candidates.py
python3 scripts/validate.py
```

脚本仅在链接和核查状态满足条件时显示“推广入口（可能产生佣金）”。HTML 链接设置 sponsored nofollow。GitHub 如何最终处理页面属性由平台决定；如果后续建立独立网站，必须重新检查实际输出。

当前检查不联网，不能确认重定向后佣金归因。接入真实链接后还需打开目标入口、确认品牌和活动，再在联盟后台核对点击记录。不要自行从原作者邀请码推导你的邀请码。


## 新增的资料字段

price_status 区分 primary_current（本次官方公开价）、secondary_reference（参考价）和 unknown（没有可靠价格）。这和品牌资料的 verification_status 是两个不同状态：官方帮助页能核实规格，不一定公开现价。

offers 记录代表套餐、金额、币种、实付周期、流量口径及来源编号；sources 记录来源类型和读取日期。researched_at 是本轮检索日期，source_date_note 说明原始报价日期或缺失。修改套餐后重新生成档案，不要只改页面而遗漏数据。

价格为 unknown 的条目继续隐藏推广入口。启用推广前必须核对品牌和当期商店，删除首页与相关指南中“全部留空”等过时说明，并更新披露和核查数量。
