#!/usr/bin/env python3
"""最小 MCP stdio 客户端：列出 @amap/amap-maps-mcp-server 的工具"""
import json, os, subprocess, sys

API_KEY = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AMAP_MAPS_API_KEY", "")

def rpc(proc, method, params=None, req_id=1):
    msg = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        msg["params"] = params
    proc.stdin.write((json.dumps(msg) + "\n").encode())
    proc.stdin.flush()
    # 读响应（跳过 notifications）
    while True:
        line = proc.stdout.readline()
        if not line:
            return None
        try:
            resp = json.loads(line)
        except Exception:
            continue
        if resp.get("id") == req_id:
            return resp

env = dict(os.environ, AMAP_MAPS_API_KEY=API_KEY)
proc = subprocess.Popen(
    ["npx", "-y", "@amap/amap-maps-mcp-server"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    env=env, cwd=os.path.expanduser("~/workspace/amap-mcp"),
)

# initialize
init = rpc(proc, "initialize", {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "mini-mcp-client", "version": "1.0"},
}, req_id=1)
# initialized notification
proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
proc.stdin.flush()

# list tools
tools = rpc(proc, "tools/list", {}, req_id=2)
if tools and "result" in tools:
    for t in tools["result"].get("tools", []):
        print("-", t["name"], "|", t.get("description", "")[:60])
else:
    print("TOOLS LIST FAILED:", json.dumps(tools)[:500] if tools else "no response")
proc.terminate()

def call_tool(proc, name, args, req_id):
    return rpc(proc, "tools/call", {"name": name, "arguments": args}, req_id=req_id)
