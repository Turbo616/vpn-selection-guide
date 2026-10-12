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

