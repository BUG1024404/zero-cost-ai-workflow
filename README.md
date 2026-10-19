# zero-cost-ai-workflow · 零成本 AI 工作流

一套**每月 ¥0** 的个人 AI 工作流实战配置：免费大模型跑 Agent，配查票、地图、微信消息能力，开箱即用。

这是我自己每天在用的东西，不是 demo。每个组件都经过实战验证，维护成本就是顺手的事。

## 每月成本

| 项目 | 费用 |
|---|---|
| 大模型（OpenRouter 免费模型） | ¥0 |
| Pi agent 本体 | ¥0（开源） |
| 12306 查票 MCP | ¥0 |
| 高德地图 MCP | ¥0（官方免费额度） |
| 微信消息桥接 | ¥0 |
| 每日免费模型扫描 | ¥0 |
| **合计** | **¥0** |

## 包含什么

```
zero-cost-ai-workflow/
├── pi/                 # Pi agent + OpenRouter 免费模型配置（fail-closed 防扣费）
├── mcp-servers/        # 给 Agent 接外部能力：12306 查票、高德地图
├── wechat-bridge/      # 微信 ClawBot 桥接：手机微信收发 Agent 消息
└── freetoken-scan/     # 每天自动扫描 OpenRouter 免费模型，池子变了第一时间知道
```

| 组件 | 一句话 | 文档 |
|---|---|---|
| Pi + 免费模型 | 用 OpenRouter `:free` 模型跑 coding agent，配错模型自动拒绝，绝不误触收费 | [pi/README.md](pi/README.md) |
| 12306 MCP | 查余票、查车次、查站点，只查不买 | [mcp-servers/12306/README.md](mcp-servers/12306/README.md) |
| 高德 MCP | 地理编码、路线规划、POI 搜索（官方 MCP） | [mcp-servers/amap/README.md](mcp-servers/amap/README.md) |
| 微信桥接 | 手机微信扫码登录，Agent 可收发微信消息 | [wechat-bridge/README.md](wechat-bridge/README.md) |
| 免费模型扫描 | 每天 08:00 扫一遍免费模型池，有变化就更新配置 | [freetoken-scan/README.md](freetoken-scan/README.md) |

## 快速开始

```bash
git clone https://github.com/<你的用户名>/zero-cost-ai-workflow.git
cd zero-cost-ai-workflow
cp .env.example .env   # 填入你的 key（只存本地，绝不提交）
```

然后按顺序看各组件的 README：`pi/` → `mcp-servers/` → `wechat-bridge/` → `freetoken-scan/`。

## 核心原则

1. **fail-closed**：模型 ID 必须命中最新免费扫描结果，否则拒绝执行。手抖少打 `:free` 后缀会路由到收费版——这条规则就是为防这个。
2. **密钥不进仓库**：所有 key 走环境变量或 600 权限的独立文件，`.gitignore` 已配好。提交前请再扫一遍。
3. **免费额度是动态的**：OpenRouter 的免费模型池经常变，`freetoken-scan/` 每天自动扫，别用一份配置吃到老。

## 致谢

- [limin112/min-skill](https://github.com/limin112/min-skill)：FreeToken-Bots 免费模型扫描方案
- [tencent/openclaw-weixin](https://github.com/tencent/openclaw-weixin)：微信桥接的官方协议实现
- [Joooook/12306-mcp](https://github.com/Joooook/12306-mcp)：12306 查票 MCP 服务端
- 高德官方 [@amap/amap-maps-mcp-server](https://www.npmjs.com/package/@amap/amap-maps-mcp-server)

## License

MIT，见 [LICENSE](LICENSE)。
