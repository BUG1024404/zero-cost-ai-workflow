#!/usr/bin/env python3
"""调用 @amap/amap-maps-mcp-server 的指定工具。用法: amap_call.py <tool> '<json_args>'"""
import json, os, subprocess, sys

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
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    key = os.environ.get("AMAP_MAPS_API_KEY", "")
    if not key:
        print(json.dumps({"error": "AMAP_MAPS_API_KEY not set"}))
        sys.exit(1)
    env = dict(os.environ, AMAP_MAPS_API_KEY=key)
    proc = subprocess.Popen(
        ["npx", "-y", "@amap/amap-maps-mcp-server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env,
    )
    rpc(proc, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "amap-call", "version": "1.0"}}, 1)
    proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
    proc.stdin.flush()
    resp = rpc(proc, "tools/call", {"name": tool, "arguments": args}, 2)
    proc.terminate()
    try:
        print(resp["result"]["content"][0]["text"])
    except Exception:
        print(json.dumps(resp, ensure_ascii=False)[:2000])

if __name__ == "__main__":
    main()
