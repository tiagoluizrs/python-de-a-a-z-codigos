"""Gabarito do exercício 4: statistics + Counter."""
import statistics
from collections import Counter


def text_stats(text: str) -> dict:
    words = text.lower().split()
    if not words:
        # statistics.mean/median levantam StatisticsError em dados vazios
        return {"words": 0, "unique": 0, "mean_len": 0.0,
                "median_len": 0, "top": []}
    counts = Counter(words)
    lengths = [len(w) for w in words]
    return {
        "words": len(words),
        "unique": len(counts),
        "mean_len": round(statistics.fmean(lengths), 2),
        "median_len": statistics.median(lengths),
        "top": counts.most_common(2),   # empates: ordem de inserção
    }
