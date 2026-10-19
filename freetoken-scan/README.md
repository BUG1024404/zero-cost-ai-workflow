# freetoken-scan · 每日免费模型扫描

OpenRouter 的免费模型池经常变：今天免费的明天可能收费，新的免费旗舰也可能突然上架。靠人肉记 ID 会吃亏，所以每天自动扫一遍。

## 方案

直接用 [limin112/min-skill](https://github.com/limin112/min-skill) 的 **FreeToken-Bots** skill，本仓库不重复造轮子：

```bash
# 装 min-skill（按需取 skill，不用全装）
git clone https://github.com/limin112/min-skill.git ~/min-skill

# 扫一遍（输出报告到 ~/.pi/agent/freetoken-bots.json）
cd ~/min-skill/skills/FreeToken-Bots
python3 scripts/radar.py scan

# 看状态
python3 scripts/radar.py status
```

扫描逻辑（保守策略）：

- 只有 `pricing.prompt == 0` 且 `pricing.completion == 0` 才算免费，动态判定，不承诺永久免费。
- 参数量 ≥100B 且**实测验证过**的才进旗舰池；API 没给参数量的放待核验区，不猜。
- 进生产前必须**独立 probe 试调用**验证工具调用能力，普通补全通过不算数。
- **fail-closed**：probe 只认最新扫描结果里的 ID；缺 `:free` 后缀的自动纠正并大声警告（曾经有人因此误触收费版）；其他 ID 直接拒绝。

## 定时任务

每天 08:00 自动扫，用 [scan.sh](scan.sh)，加进 crontab：

```cron
0 8 * * * /path/to/zero-cost-ai-workflow/freetoken-scan/scan.sh
```

报告写到 `~/.pi/agent/freetoken-bots.json`，格式示例：

```json
{
  "checked_at": "2026-10-15T00:00:21+00:00",
  "eligible": [],
  "needs_parameter_verification": [
    {"id": "nvidia/nemotron-3-super-120b-a12b:free", "context_length": 262144}
  ],
  "free_ids": ["cohere/north-mini-code:free", "..."]
}
```

## 扫到变化怎么办

1. 有新的免费旗舰模型 → 先 `probe` 试调用验证 → 验证过再写进 Pi 的 `enabledModels`。
2. 正在用的模型变收费 → 从 `enabledModels` 里拿掉，fail-closed 会拦住误用。
3. 扫描超过 24 小时没跑 → 先扫再配，别用过期报告。

## 花钱了算谁的

算你自己的。所以 `pi/settings.json` 的 `enabledModels` 只放免费 ID，详见 [../pi/README.md](../pi/README.md) 的两个坑。
