# 12306 MCP · 查票

基于 [Joooook/12306-mcp](https://github.com/Joooook/12306-mcp) 的查票能力。

**先说清楚：只能查票，不能下单、不能抢票。**下单接口上游还没做，抢票请走 12306 官方候补。这是上游的现状，不是本仓库的限制。

## 安装

```bash
cd mcp-servers/12306
npm install    # 装服务端依赖（12306-mcp）
```

## 7 个工具

| 工具 | 干什么 |
|---|---|
| `get-current-date` | 取当前日期（查票要传日期，先拿这个） |
| `get-stations-code-in-city` | 查某城市的所有车站 |
| `get-station-code-of-citys` | 批量查多个城市的车站代码 |
| `get-station-code-by-names` | 按站名查车站代码 |
| `get-station-by-telecode` | 按电报码反查车站 |
| `get-tickets` | 查余票（核心） |
| `get-interline-tickets` | 查中转票 |
| `get-train-route-stations` | 查某车次的经停站 |

## 调用示例

```bash
# 查南京到常州今天的余票（先拿日期和站点代码，再查票）
python3 12306_call.py get-current-date '{}'
python3 12306_call.py get-station-code-by-names '{"names": ["南京", "常州"]}'
python3 12306_call.py get-tickets '{"from_station": "NJH", "to_station": "CZH", "date": "2026-10-16"}'
```

用法统一：`12306_call.py <工具名> '<JSON参数>'`。无参数的工具传 `'{}'`。

## 服务端路径

`12306_call.py` 默认用本目录相对路径找服务端：

```
mcp-servers/12306/node_modules/12306-mcp/build/index.js
```

如需指定其他位置，设环境变量 `MCP_12306_SERVER`。

## 实测

南京→常州余票查询实测通过。12306 接口偶尔抽风，查不到先重试一次，再不行就是上游的问题。
