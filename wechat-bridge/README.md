# 微信桥接 · 手机微信收发 Agent 消息

基于腾讯官方 [tencent/openclaw-weixin](https://github.com/tencent/openclaw-weixin) 的 iLink 协议，自研的轻量桥接脚本（300 行，零依赖，只用 Python 标准库 + curl）。

用途：手机微信扫码登录后，Agent 可以**收微信消息、给微信发消息**。人在外面，Agent 在家干活，微信就是遥控器。

## 前置条件

手机微信 → 设置 → 插件 → 启用 **ClawBot**。

## 四个子命令

```bash
# 1. 登录：取二维码，手机微信扫码，2 分钟内有效
python3 bridge.py login

# 2. 查状态：会话是否有效、token 是否过期
python3 bridge.py status

# 3. 拉消息：JSON 输出新消息，游标自动持久化
python3 bridge.py poll

# 4. 发消息：给绑定的微信号发文本
python3 bridge.py send --text '你好'
```

`poll` 输出示例（JSON）：

```json
{"messages": [{"from_user_id": "...", "text": "帮我查下明天南京到常州的票", "create_time_ms": 1234567890}], "bound_user": "..."}
```

## 凭据安全

- 登录会话只存 `state/session.json`，**600 权限**，`.gitignore` 已排除，绝不提交。
- 轮询游标存 `state/cursor.txt`，同样不进仓库。
- 退出登录：删掉 `state/` 目录即可。

## 实测与取舍

- 收发消息、语音转文字全流程实测通过。
- 一个实战经验：本机 Python 直连 iLink 服务器会被掐连接，所以脚本统一走 `curl` 子进程——别改成 requests 直连，会挂。
- 这是我"试试"性质的项目：代码留着能用，但我没让它常驻。如果你要 7×24 跑，自己加个 cron 轮询 `poll`。

## 风险提示

这是非官方客户端实现，依赖微信 iLink 协议。协议变了就得跟着改，不保证长期可用。别拿它做关键业务通知的唯一通道。
