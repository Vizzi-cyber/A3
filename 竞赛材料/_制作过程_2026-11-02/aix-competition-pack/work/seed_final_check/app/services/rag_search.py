"""
知识库 RAG 语义检索服务
算法：BM25（Okapi BM25 概率检索模型，自实现）+ jieba 中文分词
  - 对笔记（标题+正文）建 BM25 索引
  - 查询分词后按 BM25 得分排序（信息检索经典算法，RAG 检索阶段常用）
  - 提取命中片段（关键词上下文 ±60 字），供 LLM/前端引用
不依赖外部 LLM API——检索阶段纯本地算法，可写进技术方案。
"""
import math
import re
from typing import Any, Dict, List

import jieba

# 常用停用词（单字 + 虚词，字间用空格分隔）
_STOPWORDS = {
    "的", "了", "和", "与", "就", "都", "而", "及", "或", "个", "一", "在", "上",
    "也", "这", "那", "是", "会", "以", "有", "对", "于", "我们", "中", "到",
    "把", "被", "从", "为", "并", "要", "等", "他", "我", "你", "她", "它",
    "如果", "因为", "所以", "但是", "然而", "并且", "非常", "可能", "应该",
    "可以", "已经", "通过", "根据", "随着", "其中", "以及", "超过", "不到",
    "什么", "怎么", "如何", "为什么", "这个", "那个", "一种", "进行",
}


def tokenize(text: str) -> List[str]:
    """jieba 分词 + 停用词过滤 + 小写。"""
    if not text:
        return []
    words = []
    for w in jieba.cut(text):
        w = w.strip().lower()
        if not w or w in _STOPWORDS:
            continue
        if re.fullmatch(r"[^\u4e00-\u9fa5a-zA-Z0-9]+", w):
            continue
        words.append(w)
    return words


class RAGSearchEngine:
    """基于 BM25 的知识库语义检索引擎（按学生实例化）。"""

    def __init__(self) -> None:
        self._docs: List[Dict[str, Any]] = []
        self._tokenized: List[List[str]] = []
        self._N = 0
        self._df: Dict[str, int] = {}
        self._avgdl = 1.0
        self._ready = False

    def build(self, notes: List[Dict[str, Any]]) -> None:
        """构建 BM25 索引。notes: [{note_id, title, content, folder_id}]"""
        self._docs = []
        self._tokenized = []
        for n in notes:
            text = f"{n.get('title', '')} {n.get('content', '')}"
            tokens = tokenize(text)
            if not tokens:
                tokens = [n.get("title", "")[:1] or "x"]
            self._docs.append(n)
            self._tokenized.append(tokens)

        self._N = len(self._docs)
        self._df = {}
        total_len = 0
        if self._N:
            for tokens in self._tokenized:
                total_len += len(tokens)
                for w in set(tokens):
                    self._df[w] = self._df.get(w, 0) + 1
            self._avgdl = total_len / self._N
        self._ready = self._N > 0

    @property
    def is_ready(self) -> bool:
        return self._ready

    def _bm25_score(self, query_tokens: List[str], doc_idx: int, k1: float = 1.5, b: float = 0.75) -> float:
        """Okapi BM25：score = Σ idf(qi) * f(qi,D)*(k1+1) / (f(qi,D) + k1*(1-b + b*|D|/avgdl))"""
        doc_tokens = self._tokenized[doc_idx]
        dl = len(doc_tokens) or 1
        tf: Dict[str, int] = {}
        for w in doc_tokens:
            tf[w] = tf.get(w, 0) + 1

        score = 0.0
        for q in set(query_tokens):
            df = self._df.get(q, 0)
            if df == 0:
                continue
            idf = math.log((self._N - df + 0.5) / (df + 0.5) + 1.0)
            f = tf.get(q, 0)
            if f == 0:
                continue
            denom = f + k1 * (1 - b + b * dl / self._avgdl)
            score += idf * (f * (k1 + 1)) / denom
        return score

    def search(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """BM25 检索：按相关度排序，含命中片段。"""
        if not self._ready:
            return []
        q_tokens = tokenize(query)
        if not q_tokens:
            return []
        scored = [(i, self._bm25_score(q_tokens, i)) for i in range(self._N)]
        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, s in scored[:top_k]:
            if s <= 0:
                continue
            doc = self._docs[idx]
            results.append({
                "note_id": doc["note_id"],
                "title": doc.get("title", ""),
                "folder_id": doc.get("folder_id"),
                "score": round(float(s), 3),
                "snippet": self._extract_snippet(doc.get("content", ""), q_tokens),
                "updated_at": doc.get("updated_at"),
            })
        return results

    @staticmethod
    def _extract_snippet(content: str, q_tokens: List[str], width: int = 60) -> str:
        """提取包含查询词的片段（命中词上下文 ±width/2 字）。"""
        if not content:
            return ""
        lower = content.lower()
        best_pos, best_word = -1, ""
        for w in q_tokens:
            pos = lower.find(w)
            if pos >= 0 and (best_pos < 0 or pos < best_pos):
                best_pos, best_word = pos, w
        if best_pos < 0:
            return content[: width * 2]
        start = max(0, best_pos - width // 2)
        end = min(len(content), best_pos + len(best_word) + width // 2)
        snippet = content[start:end]
        if start > 0:
            snippet = "…" + snippet
        if end < len(content):
            snippet += "…"
        return snippet
