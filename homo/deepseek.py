"""
DeepSeek LLM 客户端 — HOMO 记忆系统的 LLM 接口

提供与 DeepSeek 系列模型（API 版和本地版）的通信能力。
用于记忆压缩、实体提取、检索重排等需要 LLM 的场景。

支持的模型:
  - DeepSeek-V2 / DeepSeek-V3 / DeepSeek-R1 (API)
  - DeepSeek-R1 本地 (Ollama)
  - 其他 OpenAI 兼容 API
"""

import json
import logging
import os
from typing import Optional, List, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import URLError

from .config import get_config

logger = logging.getLogger("homo")


class DeepSeekClient:
    """DeepSeek LLM 客户端。

    支持 API 模式和本地 Ollama 模式。

    Usage:
        client = DeepSeekClient()
        response = client.chat("你好，请帮我压缩这段记忆...")
    """

    def __init__(self, config=None):
        self.config = config or get_config()

        # API 模式配置
        self.api_key = self.config.get("deepseek_api_key", "")
        self.api_base = self.config.get("deepseek_api_base",
                                         "https://api.deepseek.com")
        self.api_model = self.config.get("deepseek_model", "deepseek-chat")

        # 本地模式配置
        self.ollama_base = self.config.get("ollama_base_url",
                                           "http://localhost:11434")
        self.ollama_model = self.config.get("ollama_model", "deepseek-r1:7b")

        self.use_local = self.config.get("use_local_llm", True)

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 4096) -> Optional[str]:
        """发送聊天请求。

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大生成长度

        Returns:
            LLM 回复文本，失败返回 None
        """
        if self.use_local and not self.api_key:
            return self._chat_ollama(messages, temperature, max_tokens)
        elif self.api_key:
            return self._chat_api(messages, temperature, max_tokens)
        else:
            logger.warning("未配置 LLM（既没有 API key，也没有本地模型）")
            return None

    def _chat_api(self, messages, temperature, max_tokens):
        """通过 DeepSeek API 发送请求。"""
        url = f"{self.api_base}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "model": self.api_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = Request(url, data=data, headers=headers, method="POST")
            with urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
        except URLError as e:
            logger.error(f"DeepSeek API 请求失败: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"DeepSeek API 响应解析失败: {e}")
            return None

    def _chat_ollama(self, messages, temperature, max_tokens):
        """通过本地 Ollama 发送请求。"""
        url = f"{self.ollama_base}/api/chat"
        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = Request(url, data=data, headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
            return result["message"]["content"]
        except URLError as e:
            logger.error(f"Ollama 请求失败: {e}\n请确认 Ollama 正在运行: ollama serve")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Ollama 响应解析失败: {e}")
            return None

    def compress_memory(self, text: str) -> Optional[str]:
        """用 AAAK 格式压缩记忆文本。

        Args:
            text: 原始文本

        Returns:
            AAAK 格式的压缩文本
        """
        system_prompt = """你是一个记忆压缩专家。请将以下对话/文本压缩为 AAAK(Adaptive AI-Aware Key)格式。
AAAK格式：SESSION:YYYY-MM-DD|实体编码列表|元数据|★情感标记

规则：
- 提取关键实体和事件
- 用竖线分隔不同维度
- 加★标记重要性（★一般 ★★重要 ★★★关键）
- 保持事实准确性，不编造
- 中文输出"""
        return self.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ], temperature=0.3, max_tokens=1024)

    def extract_entities(self, text: str) -> Optional[List[Dict]]:
        """从文本中提取实体关系。

        Returns:
            [{"subject": "...", "predicate": "...", "object": "...", "importance": "high"}]
        """
        system_prompt = """从以下文本中提取实体关系三元组。
输出 JSON 数组格式：[{"subject": "实体A", "predicate": "关系", "object": "实体B", "importance": "high|medium|low"}]
只返回 JSON，不要其他文字。中文输出。"""
        result = self.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ], temperature=0.1, max_tokens=2048)
        if result:
            try:
                # 尝试从 Markdown 代码块中提取
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0].strip()
                return json.loads(result)
            except (json.JSONDecodeError, IndexError):
                logger.warning("实体提取 JSON 解析失败")
        return None

    def rerank(self, query: str, candidates: List[str], top_k: int = 3) -> Optional[List[int]]:
        """用 LLM 对检索结果进行重排。

        Args:
            query: 搜索查询
            candidates: 候选文本列表
            top_k: 返回最相关的 k 个索引

        Returns:
            重排后的最佳索引列表
        """
        prompt = f"""查询: {query}

候选记忆:
"""
        for i, c in enumerate(candidates):
            prompt += f"\n[{i}] {c[:200]}"

        prompt += "\n\n请按相关性排序，返回最相关的 top-3 编号（如 [2, 0, 1]）。只返回列表。"

        result = self.chat([
            {"role": "user", "content": prompt},
        ], temperature=0.1, max_tokens=100)

        if result:
            try:
                import re
                nums = re.findall(r'\d+', result)
                indices = [int(n) for n in nums if int(n) < len(candidates)]
                return indices[:top_k]
            except Exception:
                logger.warning("重排结果解析失败")
        return list(range(min(top_k, len(candidates))))


def get_deepseek_client() -> DeepSeekClient:
    """获取全局 DeepSeek 客户端实例。"""
    return DeepSeekClient()
