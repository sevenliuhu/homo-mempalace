#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HOMO-MemPalace 一键安装脚本
# DeepSeek 版本地优先 AI 记忆系统
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

echo "🧠 HOMO-MemPalace 安装开始..."
echo ""

# ── 检查 Python ──
PYTHON_VERSION=$(python3 --version 2>/dev/null || true)
if [ -z "$PYTHON_VERSION" ]; then
    echo "❌ 未找到 Python 3.9+，请先安装 Python"
    exit 1
fi
echo "✅ Python: $PYTHON_VERSION"

# ── 检查/安装 uv ──
if command -v uv &>/dev/null; then
    echo "✅ uv: $(uv --version)"
else
    echo "📦 安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# ── 安装 mempalace ──
echo "📦 安装 mempalace..."
uv tool install mempalace --quiet 2>/dev/null || pip install mempalace --quiet

# ── 安装 HOMO 适配层 ──
echo "📦 安装 HOMO 适配层..."
cd "$(dirname "$0")/.."
pip install -e . --quiet

# ── 初始化 ──
echo "🔧 初始化 HOMO 记忆宫殿..."
homo-mempalace init

# ── 检查 DeepSeek ──
echo ""
echo "🔍 检测 DeepSeek 环境..."
if command -v ollama &>/dev/null; then
    echo "✅ 已检测到 Ollama（本地推理引擎）"
    echo "   如需使用本地 DeepSeek-R1，请运行:"
    echo "     ollama pull deepseek-r1:7b"
    echo "     homo-mempalace config set use_local_llm true"
elif [ -n "$DEEPSEEK_API_KEY" ]; then
    echo "✅ 已检测到 DEEPSEEK_API_KEY"
    echo "   如需使用 API 模式，请运行:"
    echo "     homo-mempalace config set deepseek_api_key \$DEEPSEEK_API_KEY"
else
    echo "⚠️ 未检测到 LLM 配置"
    echo "   选项1: 安装 Ollama 并使用本地模型"
    echo "     curl -fsSL https://ollama.com/install.sh | sh"
    echo "     ollama pull deepseek-r1:7b"
    echo "   选项2: 配置 DeepSeek API"
    echo "     homo-mempalace config set deepseek_api_key sk-your-key"
fi

# ── 完成 ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 HOMO-MemPalace 安装完成！"
echo ""
echo "快速开始:"
echo "  1. 摄入记忆:  homo-mempalace mine ~/projects/myapp"
echo "  2. 搜索记忆:  homo-mempalace search '你的问题'"
echo "  3. 查看状态:  homo-mempalace status"
echo ""
echo "文档: https://github.com/sevenliuhu/homo-mempalace"
echo "联系: 16208204@qq.com"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
