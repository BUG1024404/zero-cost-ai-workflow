# MCP Servers · 给 Agent 接外部能力

[MCP](https://modelcontextprotocol.io)（Model Context Protocol）是 Anthropic 推的开放协议：把外部工具（查票、地图、数据库……）包装成标准接口，任何支持 MCP 的 Agent（Pi、Claude Code 等）都能直接调用。

本仓库自带两个开箱即用的：

| 服务端 | 能力 | 费用 |
|---|---|---|
| [12306](12306/) | 查余票、查车次、查站点经停 | ¥0 |
| [amap](amap/) | 地理编码、逆编码、路线规划、POI 搜索 | ¥0（官方免费额度） |

## 两种用法

**1. 命令行直接调（推荐新手）**

每个目录下都有 `xxx_call.py`，用法统一：

```bash
python3 12306/12306_call.py <工具名> '<JSON参数>'
python3 amap/amap_call.py <工具名> '<JSON参数>'
```

不依赖 Agent，先在终端跑通，再考虑接入。

**2. 接入 Pi / Claude Code**

按各自 README 把服务端配进 Agent 的 MCP 配置即可，Agent 会自动发现工具列表。

## 自己加新的 MCP

市面上有成千上万个 MCP server（[mcp.so](https://mcp.so) 可搜）。原则：

- 优先选官方 / 大厂维护的（比如高德这个就是官方的）。
- 个人维护的先看 star 数和最近更新时间。
- 任何要你填 key 的，走环境变量，别写死在配置里。
