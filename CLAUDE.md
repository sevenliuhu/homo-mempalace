# HOMO-MemPalace — Agent Guide

## Project Overview

HOMO-MemPalace is the Chinese-enhanced version of MemPalace (52K+ stars), optimized for DeepSeek models. A local-first AI memory system using Wing-Room-Drawer architecture.

## Architecture

```
WING (人/项目) → ROOM (时间线/主题) → DRAWER (原始文本)
```

Key components:
- **homo/adaptor.py** — Memory adaptor wrapping mempalace API with Chinese interface
- **homo/deepseek.py** — DeepSeek LLM client for memory compression & entity extraction
- **homo/aaak_zh.py** — Chinese AAAK compression format
- **homo/config.py** — Configuration manager (env vars > config file > defaults)
- **homo/cli.py** — Chinese CLI with 12 commands

## Commands

```bash
homo-mempalace init                  # Initialize memory palace
homo-mempalace mine <path>           # Ingest memories
homo-mempalace search <query>        # Semantic search
homo-mempalace wake-up               # Wake-up mode (L0+L1, ~600-900 tokens)
homo-mempalace status                # Palace status
homo-mempalace config --list         # Show config
homo-mempalace kg query <entity>     # Knowledge graph query
homo-mempalace compress --text "..."  # AAAK compression
homo-mempalace hooks --install       # Install auto-save hooks
```

## Dependencies

- mempalace >= 3.3.5 (the core engine)
- Python 3.9+

No external API keys required for core function.
