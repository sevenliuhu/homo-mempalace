"""
HOMO-MemPalace 快速入门示例

演示如何使用 HOMO 记忆系统。
"""

import sys
import os

# 添加项目到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from homo.adaptor import HomoPalace
from homo.aaak_zh import AAAK_ZH


def demo():
    print("=" * 50)
    print("🧠 HOMO-MemPalace 快速入门")
    print("=" * 50)

    # 1. 初始化（需要先运行 homo-mempalace init）
    palace = HomoPalace()
    print(f"\n📍 宫殿路径: {palace.palace_path}")
    print(f"📊 记忆总数: {palace.count_memories()} 条\n")

    # 2. AAAK 压缩示例
    print("─" * 40)
    print("AAAK 压缩格式示例:")
    encoded = AAAK_ZH.encode(
        session_type="SESSION",
        entities=["项目.架构设计", "后端.API"],
        meta={"DEC": "使用 GraphQL"},
        importance=2,
    )
    print(f"  编码: {encoded}")

    decoded = AAAK_ZH.decode(encoded)
    print(f"  解码: {decoded}")

    # 日记格式
    diary = AAAK_ZH.make_diary(
        date_str="2026-05-22",
        work_items=["设计了.homo.架构", "集成了.mempalace.api"],
        meta={"ALC": "mempalace.adaptor"},
    )
    print(f"  日记: {diary}")

    # 3. 唤醒模式
    print("\n" + "─" * 40)
    print("唤醒模式（L0 + L1）:")
    wake_text = palace.wake_up()
    print(f"  输出 (~{len(wake_text)//4} tokens)")
    print(f"  前200字: {wake_text[:200]}...")

    # 4. 使用建议
    print("\n" + "─" * 40)
    print("💡 使用建议:")
    print("  1. 先运行 homo-mempalace mine <path> 摄入记忆")
    print("  2. 用 homo-mempalace search 搜索已存记忆")
    print("  3. 使用 MCP 工具集成到你的 AI 工作流")
    print()
    print("  安装原版 mempalace:")
    print("    uv tool install mempalace")
    print("    homo-mempalace mine ~/projects/myapp")
    print("    homo-mempalace search '项目架构'")
    print("=" * 50)


if __name__ == "__main__":
    demo()
