"""
HOMO CLI — 命令行接口

提供中文命令行接口，管理记忆系统。
"""

import argparse
import json
import os
import sys
from pathlib import Path

from .config import get_config, HOMO_CONFIG_DIR
from .adaptor import HomoPalace
from .deepseek import DeepSeekClient


def cmd_init(args):
    """初始化 HOMO 记忆宫殿。"""
    config = get_config()
    os.makedirs(HOMO_CONFIG_DIR, exist_ok=True)
    os.makedirs(config.palace_path, exist_ok=True)
    print(f"✅ HOMO 记忆宫殿已初始化")
    print(f"   配置目录: {HOMO_CONFIG_DIR}")
    print(f"   宫殿路径: {config.palace_path}")
    print(f"   使用以下命令摄入记忆:")
    print(f"     homo-mempalace mine ~/projects/myapp")
    print(f"     homo-mempalace mine ~/.claude/projects/ --mode convos")


def cmd_config(args):
    """管理配置。"""
    config = get_config()
    if args.get:
        val = config.get(args.get)
        if val is not None:
            print(f"{args.get} = {val}")
        else:
            print(f"配置项 '{args.get}' 不存在")
    elif args.set:
        key, value = args.set, args.value
        config.set(key, value)
        print(f"✅ {key} = {value}")
    elif args.list:
        all_cfg = config.all()
        print("当前配置:")
        for k, v in all_cfg.items():
            print(f"  {k} = {v}")
    elif args.reset:
        # 重置为默认值
        os.makedirs(HOMO_CONFIG_DIR, exist_ok=True)
        # 写默认配置
        from .config import HomoConfig
        default = HomoConfig()
        default.save()
        print("✅ 配置已重置为默认值")


def cmd_mine(args):
    """摄入记忆。"""
    palace = HomoPalace()
    result = palace.mine(
        path=args.path,
        mode=args.mode,
        wing=args.wing,
    )
    print(result)


def cmd_search(args):
    """搜索记忆。"""
    palace = HomoPalace()
    results = palace.search(
        query=args.query,
        wing=args.wing,
        room=args.room,
        n=args.limit,
    )
    if results:
        print(f"找到 {len(results)} 条相关记忆:\n")
        for i, r in enumerate(results, 1):
            print(f"  [{i}] (相似度: {r.get('similarity', 'N/A')})")
            print(f"      {r.get('text', '')[:200]}")
            print()
    else:
        # 尝试使用 CLI 搜索
        palace._run(["mempalace", "search", args.query])


def cmd_wake(args):
    """唤醒模式。"""
    palace = HomoPalace()
    text = palace.wake_up(wing=args.wing)
    tokens = len(text) // 4
    print(f"唤醒文本 (~{tokens} tokens):")
    print("=" * 50)
    print(text)


def cmd_kg(args):
    """知识图谱操作。"""
    palace = HomoPalace()
    if args.action == "query":
        results = palace.kg_query(args.entity, as_of=args.as_of)
        if results:
            print(f"实体 '{args.entity}' 的关系:")
            for r in results:
                print(f"  {r}")
        else:
            print(f"未找到实体 '{args.entity}' 的关系")
    elif args.action == "add":
        palace.kg_add(args.subject, args.predicate, args.object,
                      valid_from=args.valid_from, valid_to=args.valid_to)
        print(f"✅ 已添加: {args.subject} --{args.predicate}--> {args.object}")


def cmd_status(args):
    """查看宫殿状态。"""
    palace = HomoPalace()
    status = palace.status()
    count = palace.count_memories()

    print("🧠 HOMO 记忆宫殿状态")
    print("=" * 40)
    print(f"  记忆总数: {count} 条")
    print(f"  宫殿路径: {palace.palace_path}")
    if status.get("status"):
        print(f"  概要: {status['status']}")


def cmd_compress(args):
    """压缩文本为 AAAK 格式。"""
    from .aaak_zh import AAAK_ZH

    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    client = DeepSeekClient()
    result = client.compress_memory(text)

    if result:
        print(result)
    else:
        print("LLM 不可用，使用本地 AAAK 编码:")
        encoded = AAAK_ZH.encode(
            session_type="MEMORY",
            entities=["手动.输入"],
            importance=1,
        )
        print(encoded)


def cmd_hooks(args):
    """管理钩子。"""
    if args.install:
        install_dir = os.path.expanduser("~/.claude/hooks")
        os.makedirs(install_dir, exist_ok=True)

        hook_content = '''#!/bin/bash
# HOMO MemPalace Auto-Save Hook
# 安装: 将 hooks/ 目录链接到 ~/.claude/hooks/
mempalace mine "$MEMORY_DIR" --mode convos 2>/dev/null || true
'''
        hook_path = os.path.join(install_dir, "homo-save.sh")
        with open(hook_path, "w") as f:
            f.write(hook_content)
        os.chmod(hook_path, 0o755)
        print(f"✅ 钩子已安装: {hook_path}")
        print("   请在 Claude Code 中配置:")
        print(f"   claude mcp add homo-mempalace -- homo-mempalace mcp")

    elif args.list:
        print("已安装的钩子:")
        hook_dir = os.path.expanduser("~/.claude/hooks")
        if os.path.exists(hook_dir):
            for f in os.listdir(hook_dir):
                print(f"  {hook_dir}/{f}")
        else:
            print("  未安装钩子")

    elif args.remove:
        hook_path = os.path.join(os.path.expanduser("~/.claude/hooks"), "homo-save.sh")
        if os.path.exists(hook_path):
            os.remove(hook_path)
            print(f"✅ 钩子已移除: {hook_path}")


def cmd_mcp(args):
    """启动 MCP 服务器。"""
    try:
        from mempalace.mcp_server import main as mcp_main
        sys.argv = ["mempalace-mcp"]
        if args.palace:
            sys.argv.extend(["--palace", args.palace])
        mcp_main()
    except ImportError:
        print("请先安装 mempalace: uv tool install mempalace")


def main():
    parser = argparse.ArgumentParser(
        description="🧠 HOMO-MemPalace — DeepSeek 版本地优先 AI 记忆系统",
    )
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # init
    p_init = subparsers.add_parser("init", help="初始化记忆宫殿")

    # config
    p_config = subparsers.add_parser("config", help="管理配置")
    p_config.add_argument("--set", metavar="KEY", help="设置配置项")
    p_config.add_argument("--value", metavar="VAL", help="配置项值")
    p_config.add_argument("--get", metavar="KEY", help="获取配置项")
    p_config.add_argument("--list", action="store_true", help="列出所有配置")
    p_config.add_argument("--reset", action="store_true", help="重置为默认配置")

    # mine
    p_mine = subparsers.add_parser("mine", help="摄入记忆")
    p_mine.add_argument("path", help="项目路径或对话路径")
    p_mine.add_argument("--mode", choices=["files", "convos"], default="files",
                        help="摄入模式：files（项目文件）或 convos（对话记录）")
    p_mine.add_argument("--wing", help="指定翼名")

    # search
    p_search = subparsers.add_parser("search", help="搜索记忆")
    p_search.add_argument("query", help="搜索关键词")
    p_search.add_argument("--wing", help="限定翼")
    p_search.add_argument("--room", help="限定房间")
    p_search.add_argument("--limit", type=int, default=5, help="返回结果数")

    # wake
    p_wake = subparsers.add_parser("wake-up", help="唤醒模式（L0+L1）")
    p_wake.add_argument("--wing", help="按项目唤醒")

    # kg
    p_kg = subparsers.add_parser("kg", help="知识图谱操作")
    p_kg_sub = p_kg.add_subparsers(dest="action", help="KG操作")
    p_kg_query = p_kg_sub.add_parser("query", help="查询实体")
    p_kg_query.add_argument("entity", help="实体名")
    p_kg_query.add_argument("--as-of", help="时间点（YYYY-MM-DD）")
    p_kg_add = p_kg_sub.add_parser("add", help="添加事实")
    p_kg_add.add_argument("subject", help="主体")
    p_kg_add.add_argument("predicate", help="关系")
    p_kg_add.add_argument("object", help="客体")
    p_kg_add.add_argument("--valid-from", help="开始时间")
    p_kg_add.add_argument("--valid-to", help="结束时间")

    # status
    p_status = subparsers.add_parser("status", help="宫殿状态")

    # compress
    p_compress = subparsers.add_parser("compress", help="压缩为 AAAK 格式")
    p_compress.add_argument("--text", help="要压缩的文本")
    p_compress.add_argument("--file", help="从文件读取文本")

    # hooks
    p_hooks = subparsers.add_parser("hooks", help="管理钩子")
    p_hooks.add_argument("--install", action="store_true", help="安装钩子")
    p_hooks.add_argument("--list", action="store_true", help="列出钩子")
    p_hooks.add_argument("--remove", action="store_true", help="移除钩子")

    # mcp
    p_mcp = subparsers.add_parser("mcp", help="启动 MCP 服务器")
    p_mcp.add_argument("--palace", help="宫殿路径")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "config":
        cmd_config(args)
    elif args.command == "mine":
        cmd_mine(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "wake-up":
        cmd_wake(args)
    elif args.command == "kg":
        cmd_kg(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "compress":
        cmd_compress(args)
    elif args.command == "hooks":
        cmd_hooks(args)
    elif args.command == "mcp":
        cmd_mcp(args)
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover
    main()
