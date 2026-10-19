# 高德地图 MCP · 查路线找地方

基于高德官方的 [@amap/amap-maps-mcp-server](https://www.npmjs.com/package/@amap/amap-maps-mcp-server)。

## 申请 Key（有免费额度）

1. 去 https://console.amap.com 注册并创建一个应用，拿到 API Key。
2. **Key 只用一次、不存文件**：每次调用前在终端里 export，用完即走。

```bash
export AMAP_MAPS_API_KEY='你的key'
```

别把 key 写进任何文件、别提交到 git。

## 两个脚本

| 脚本 | 干什么 |
|---|---|
| `amap_call.py` | 调指定工具：`amap_call.py <工具名> '<JSON参数>'` |
| `mcp_client.py` | 列出服务端所有可用工具（先跑这个看有什么） |

```bash
# 先看有哪些工具
python3 mcp_client.py

# 地理编码示例
python3 amap_call.py maps_geo '{"address": "常州市钟楼区", "city": "常州"}'

# 路线规划、POI 搜索等，参数看 mcp_client.py 列出的工具说明
```

## 工具列表（以 mcp_client.py 实际输出为准）

常用：地理编码 / 逆地理编码、步行 / 驾车 / 公交路线规划、周边 POI 搜索、天气查询等。

## 实测

公司地址缺失时查导航、规划拜访路线实测可用。高德免费额度对个人日常用量绰绰有余。
