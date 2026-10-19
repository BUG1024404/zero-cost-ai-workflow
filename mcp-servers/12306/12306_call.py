#!/usr/bin/env python3
"""调用 12306-mcp 的指定工具。用法: 12306_call.py <tool> '<json_args>'
工具: get-current-date, get-stations-code-in-city, get-station-code-of-citys,
      get-station-code-by-names, get-station-by-telecode, get-tickets,
      get-interline-tickets, get-train-route-stations

服务端路径：优先取环境变量 MCP_12306_SERVER，否则用本脚本所在目录下的
node_modules/12306-mcp/build/index.js（先在目录里跑 npm install）。
"""
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_JS = os.environ.get("MCP_12306_SERVER") or os.path.join(
    BASE_DIR, "node_modules", "12306-mcp", "build", "index.js"
)
SERVER = ["node", SERVER_JS]


def rpc(proc, method, params, req_id):
    proc.stdin.write((json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}) + "\n").encode())
    proc.stdin.flush()
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


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if not os.path.exists(SERVER_JS):
        print(json.dumps({"error": f"12306-mcp server not found: {SERVER_JS}; run 'npm install' in {BASE_DIR} first"},
                         ensure_ascii=False))
        sys.exit(1)
    proc = subprocess.Popen(SERVER, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    rpc(proc, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "12306-call", "version": "1.0"}}, 1)
    proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
    proc.stdin.flush()
    resp = rpc(proc, "tools/call", {"name": tool, "arguments": args}, 2)
    proc.terminate()
    try:
        print(resp["result"]["content"][0]["text"])
    except Exception:
        print(json.dumps(resp, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
