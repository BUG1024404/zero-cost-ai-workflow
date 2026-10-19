# Pi + OpenRouter 免费模型

[Pi](https://pi.dev) 是一个开源的 coding agent，用它搭配 OpenRouter 的免费模型，日常写代码、跑任务一分钱不花。

## 安装

```bash
# 官方安装脚本（推荐）
curl -fsSL https://pi.dev/install.sh | sh
# 重启 shell 后验证
pi --version
```

备选（需要 Node.js ≥ 22.19）：

```bash
npm install -g @earendil-works/pi-coding-agent
pi --version
```

注意：Pi 的配置在 `~/.pi/agent/` 下（VM 重置后配置还在，但 `pi` 二进制可能丢，丢了重装即可）。

## 配置 OpenRouter

1. 去 https://openrouter.ai 注册并申请一个 API Key。
2. Key **不要**直接写进配置文件。存成 600 权限的独立文件：

```bash
echo -n '你的key' > ~/.pi/agent/.openrouter_key
chmod 600 ~/.pi/agent/.openrouter_key
```

3. 在 `~/.pi/agent/auth.json` 里用 `!cat` 引用（key 本体不进任何配置文件）：

```json
{
  "openrouter": {
    "type": "api_key",
    "key": "!cat ~/.pi/agent/.openrouter_key"
  }
}
```

## settings.json

把 [settings.json.example](settings.json.example) 拷到 `~/.pi/agent/settings.json`，按需改模型：

```json
{
  "defaultProvider": "openrouter",
  "defaultModel": "nvidia/nemotron-3-super-120b-a12b:free",
  "enabledModels": ["openrouter/nvidia/nemotron-3-super-120b-a12b:free"]
}
```

三个字段的意思：

- `defaultProvider`：默认走 openrouter。
- `defaultModel`：默认模型。**注意：这里不能带 provider 前缀**，必须和 `defaultProvider` 分开写。
- `enabledModels`：允许使用的模型白名单，**这里要带 `openrouter/` 前缀**。只放免费模型 = fail-closed，想花钱都花不出去。

### 两个实战踩过的坑

1. **`defaultModel` 带了 provider 前缀会被静默忽略**，然后 fallback 到收费模型，实测触发过 402 扣费。`defaultProvider` 和 `defaultModel` 必须分开写，这是铁律。
2. **`enabledModels` 只放 `:free` 模型**。某天手抖配错、或者复制了个不带 `:free` 的 ID，Pi 会直接拒绝而不是偷偷走收费版。

## 验证

```bash
pi --list-models   # 确认安装健康
```

然后跑个简单任务，确认走的是免费模型且不扣费。OpenRouter 后台可以查用量，`:free` 模型账单应为 0。

## 免费模型去哪找

OpenRouter 的免费池经常变，不要背 ID。看 [../freetoken-scan/README.md](../freetoken-scan/README.md)，每天自动扫一遍，池子变了第一时间知道。
