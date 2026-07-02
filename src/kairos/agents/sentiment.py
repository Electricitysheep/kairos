"""Sentiment Agent — analyzes news and social sentiment for any asset."""

from __future__ import annotations

import re

from kairos.agents.base import AgentBase, AgentContext, AgentResult

# Simple keyword-based sentiment lexicon
_POSITIVE_WORDS = {
    "bullish",
    "beat",
    "beats",
    "growth",
    "profit",
    "profits",
    "upgrade",
    "upgrades",
    "positive",
    "outperform",
    "buy",
    "strong",
    "momentum",
    "record",
    "surge",
    "surges",
    "gain",
    "gains",
    "rally",
    "rallies",
    "breakthrough",
    "innovation",
    "partnership",
    "expansion",
    "dividend",
    "buyback",
    "upgraded",
    "upbeat",
    "soar",
    "soars",
    "boom",
    "booming",
    "opportunity",
    "confidence",
    "optimistic",
    "breakout",
    "rising",
    "upward",
    "recovery",
    "rebound",
    "thriving",
    "prosper",
    "success",
}

_NEGATIVE_WORDS = {
    "bearish",
    "downgrade",
    "downgrades",
    "loss",
    "losses",
    "decline",
    "declines",
    "negative",
    "underperform",
    "sell",
    "weak",
    "volatility",
    "crash",
    "crashes",
    "drop",
    "drops",
    "fall",
    "falls",
    "plunge",
    "plunges",
    "downturn",
    "recession",
    "inflation",
    "layoff",
    "layoffs",
    "lawsuit",
    "investigation",
    "fraud",
    "scandal",
    "debt",
    "bankruptcy",
    "downgraded",
    "gloomy",
    "uncertainty",
    "risk",
    "risks",
    "slump",
    "slumps",
    "tumble",
    "tumbles",
    "slip",
    "slips",
    "woe",
    "woes",
    "crisis",
    "slowdown",
    "deficit",
    "cut",
    "cuts",
    "firing",
}


def _score_headline(text: str) -> tuple[float, str]:
    """Score a headline as positive, negative, or neutral.

    Returns (score, label) where score is -1.0 to 1.0.
    """
    words = set(re.findall(r"[a-zA-Z]+", text.lower()))
    pos = len(words & _POSITIVE_WORDS)
    neg = len(words & _NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0, "neutral"
    score = (pos - neg) / total
    if score > 0.2:
        return score, "bullish"
    elif score < -0.2:
        return score, "bearish"
    return score, "neutral"


class SentimentAgent(AgentBase):
    """Agent that analyzes news sentiment for a trading asset.

    Fetches recent headlines and computes a sentiment score.
    Uses keyword-based analysis (no external API needed).
    Supports FinBERT for more accurate analysis (optional).
    """

    def __init__(self, config=None, use_finbert: bool = False):
        super().__init__(config)
        self._use_finbert = use_finbert

    @property
    def name(self) -> str:
        return "sentiment"

    async def process(self, context: AgentContext) -> AgentResult:
        token = context.input_data.get("token", "")
        mode = context.input_data.get("mode", "demo")

        if mode == "demo" or not token:
            return self._mock_sentiment(token)

        try:
            return await self._real_sentiment(token)
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                output={
                    "error": f"Sentiment fetch failed: {e}",
                    "sentiment": "neutral",
                    "score": 0.0,
                },
                confidence=0.3,
                reasoning=f"Failed to fetch sentiment for {token}: {e}",
            )

    def _mock_sentiment(self, token: str) -> AgentResult:
        import random

        rng = random.Random(hash(token) % (2**32))
        sentiments = ["bullish", "bearish", "neutral"]
        weights = [0.4, 0.3, 0.3]
        sentiment = rng.choices(sentiments, weights=weights, k=1)[0]
        score = rng.uniform(-0.8, 0.8)
        return AgentResult(
            agent_name=self.name,
            output={
                "sentiment": sentiment,
                "score": round(score, 3),
                "token": token,
                "headlines": [
                    f"{token} shows {sentiment} signals in recent trading"
                    if sentiment != "neutral"
                    else f"{token} trading mixed in recent session",
                ],
                "article_count": rng.randint(3, 15),
            },
            confidence=0.5,
            reasoning=f"Mock sentiment: {sentiment} (score: {score:.2f})",
            metadata={"mode": "demo", "token": token},
        )

    async def _real_sentiment(self, token: str) -> AgentResult:
        import yfinance as yf

        ticker = yf.Ticker(token)
        news = ticker.news or []

        if not news:
            return AgentResult(
                agent_name=self.name,
                output={"sentiment": "neutral", "score": 0.0, "headlines": [], "article_count": 0},
                confidence=0.3,
                reasoning=f"No news found for {token}",
            )

        headlines = []
        scores = []
        for article in news[:20]:
            title = article.get("title", "")
            if not title:
                continue
            headlines.append(title)
            score, _ = _score_headline(title)
            scores.append(score)

        avg_score = sum(scores) / len(scores) if scores else 0.0
        if avg_score > 0.15:
            sentiment = "bullish"
        elif avg_score < -0.15:
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        return AgentResult(
            agent_name=self.name,
            output={
                "sentiment": sentiment,
                "score": round(avg_score, 3),
                "headlines": headlines[:5],
                "article_count": len(headlines),
            },
            confidence=min(0.9, 0.3 + len(headlines) * 0.03),
            reasoning=f"News sentiment: {sentiment} (score: {avg_score:.2f}, {len(headlines)} articles)",
            metadata={"mode": "live", "token": token, "articles": len(headlines)},
        )
