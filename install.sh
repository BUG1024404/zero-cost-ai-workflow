#!/usr/bin/env bash
# zero-cost-ai-workflow 一键安装脚本 (v0.2)
#
# 用法一（推荐，一条命令）：
#   curl -fsSL https://raw.githubusercontent.com/BUG1024404/zero-cost-ai-workflow/main/install.sh | bash
# 用法二（已 clone 仓库）：
#   ./install.sh
#
# 只写这几个位置，绝不碰系统目录：
#   ~/.zw/            程序与虚拟环境
#   ~/.config/zw/     配置与 Key（Key 文件 600 权限）
#   ~/.pi/agent/      Pi 的配置（auth.json / settings.json，会先备份）
set -euo pipefail

ZW_VERSION="0.2.0"
REPO_URL="https://github.com/BUG1024404/zero-cost-ai-workflow.git"
ZW_BIN="$HOME/.zw/bin"
ZW_VENV="$HOME/.zw/venv"
ZW_CONF="$HOME/.config/zw"
KEY_FILE="$ZW_CONF/.openrouter_key"
PI_BIN_DIR="$HOME/.pi/agent/bin"

info()  { printf '\033[1;34m[zw]\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m[zw] ✅\033[0m %s\n' "$*"; }
warn()  { printf '\033[1;33m[zw] ⚠️\033[0m %s\n' "$*" >&2; }
die()   { printf '\033[1;31m[zw] ❌\033[0m %s\n' "$*" >&2; exit 1; }

# ---------- 0. 定位仓库 ----------
SCRIPT_SRC="${BASH_SOURCE[0]:-}"
if [[ -n "$SCRIPT_SRC" && -f "$(dirname "$SCRIPT_SRC")/zw" ]]; then
  REPO_DIR="$(cd "$(dirname "$SCRIPT_SRC")" && pwd)"
  info "使用本地仓库：$REPO_DIR"
else
  info "管道模式：clone 仓库到 ~/.zw/src/zero-cost-ai-workflow"
  command -v git >/dev/null 2>&1 || die "需要 git，请先安装 git 后重试"
  REPO_DIR="$HOME/.zw/src/zero-cost-ai-workflow"
  if [[ -d "$REPO_DIR/.git" ]]; then
    git -C "$REPO_DIR" pull --ff-only -q || warn "仓库更新失败，继续用现有版本"
  else
    mkdir -p "$(dirname "$REPO_DIR")"
    git clone --depth 1 "$REPO_URL" "$REPO_DIR" -q
  fi
fi
[[ -f "$REPO_DIR/zw" ]] || die "仓库中找不到 zw 程序，安装中止"

# ---------- 1. 环境检查 ----------
info "检查环境…"
command -v python3 >/dev/null 2>&1 || die "找不到 python3，请先安装 Python 3.10+"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
  || die "Python 版本过低（$(python3 --version 2>&1)），需要 3.10+"
ok "Python $(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"

if command -v node >/dev/null 2>&1; then
  ok "Node.js $(node --version)"
else
  warn "未检测到 Node.js：Pi 部分功能可能受影响，可稍后安装 https://nodejs.org/（LTS）"
fi

# ---------- 2. 安装 Pi ----------
if command -v pi >/dev/null 2>&1 || [[ -x "$PI_BIN_DIR/pi" ]]; then
  ok "Pi 已安装"
else
  info "正在安装 Pi agent（官方脚本）…"
  curl -fsSL https://pi.dev/install.sh | sh
  ok "Pi 安装完成"
fi

# ---------- 3. 建目录 & 虚拟环境 ----------
mkdir -p "$ZW_BIN" "$ZW_CONF" "$HOME/.pi/agent"
chmod 700 "$ZW_CONF"
if [[ ! -d "$ZW_VENV" ]]; then
  info "创建虚拟环境 ~/.zw/venv…"
  python3 -m venv "$ZW_VENV"
fi
ok "目录就绪"

# ---------- 4. 安装 zw ----------
cp -f "$REPO_DIR/zw" "$ZW_BIN/zw"
chmod +x "$ZW_BIN/zw"
ok "zw $ZW_VERSION 已安装到 $ZW_BIN/zw"

# ---------- 5. PATH ----------
add_path_rc() {
  local line='export PATH="$HOME/.zw/bin:$PATH"'
  for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    [[ -f "$rc" ]] || continue
    grep -Fq '.zw/bin' "$rc" 2>/dev/null || { printf '\n# zero-cost-ai-workflow\n%s\n' "$line" >> "$rc"; }
  done
  # Pi 的 bin 目录也顺手加上
  local pi_line='export PATH="$HOME/.pi/agent/bin:$PATH"'
  for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    [[ -f "$rc" ]] || continue
    grep -Fq '.pi/agent/bin' "$rc" 2>/dev/null || { printf '\n# pi agent\n%s\n' "$pi_line" >> "$rc"; }
  done
}
add_path_rc
export PATH="$ZW_BIN:$PI_BIN_DIR:$PATH"

# ---------- 6. OpenRouter Key（隐藏输入，绝不打印） ----------
if [[ -f "$KEY_FILE" ]]; then
  info "Key 文件已存在，跳过输入（如需更换请删除 $KEY_FILE 后重跑）"
else
  echo
  echo "需要你的 OpenRouter API Key（免费模型也要带 key 调用，但 :free 模型不扣费）。"
  echo "去 https://openrouter.ai 注册后，在 API Keys 页面创建一个。"
  echo
  key=""
  while true; do
    printf '请粘贴 Key（输入时不显示，回车确认）: ' >&2
    IFS= read -rs key || true
    printf '\n' >&2
    # 去掉首尾空白
    key="$(printf '%s' "$key" | tr -d '[:space:]')"
    if [[ ${#key} -ge 20 ]]; then break; fi
    warn "Key 太短（${#key} 字符），请重新粘贴；按 Ctrl+C 退出。"
  done
  umask 077
  printf '%s' "$key" > "$KEY_FILE"
  chmod 600 "$KEY_FILE"
  key=""; unset key   # 内存中清除
  ok "Key 已保存（600 权限，仅本机可读）"
fi
# 兼容旧版 freetoken-scan/scan.sh 的 key 路径
if [[ ! -e "$HOME/.pi/agent/.openrouter_key" ]]; then
  ln -s "$KEY_FILE" "$HOME/.pi/agent/.openrouter_key" 2>/dev/null || true
fi

# ---------- 7. 生成 Pi 配置（fail-closed） ----------
printf 'REPO_DIR=%s\n' "$REPO_DIR" > "$ZW_CONF/install.conf"
chmod 600 "$ZW_CONF/install.conf"
"$ZW_BIN/zw" init

# ---------- 8. 首次扫描（尽力而为，失败不中断安装） ----------
info "首次扫描免费模型池（可能需要几十秒）…"
if "$ZW_BIN/zw" scan; then
  ok "免费池已同步"
else
  warn "首次扫描失败，稍后手动运行：zw scan"
fi

# ---------- 9. 体检 ----------
echo
"$ZW_BIN/zw" doctor || true

# ---------- 10. 战报 ----------
echo
echo "=============================================="
echo "  🎉 安装完成！零成本 AI 工作流就绪"
echo "=============================================="
echo "  已安装：zw $ZW_VERSION ｜ Pi agent ｜ 免费模型白名单"
echo "  每月成本：¥0（fail-closed：收费模型碰都碰不到）"
echo
echo "  上手："
echo "    zw chat            # 直接开聊"
echo "    zw scan            # 刷新免费模型池"
echo "    zw models          # 查看/切换免费模型"
echo "    zw doctor          # 体检"
echo
echo "  先重开一个终端（或执行 source ~/.bashrc）再用 zw 命令。"
echo "=============================================="
