from typing import Any, Dict, List

from src.telemetry.logger import logger


class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs.
    """

    # Rough USD per 1M tokens (input, output) — for lab cost awareness only.
    _RATES_PER_M: Dict[str, tuple] = {
        "gpt-4o": (2.5, 10.0),
        "gpt-4o-mini": (0.15, 0.6),
        "gpt-4-turbo": (10.0, 30.0),
        "gemini-1.5-flash": (0.075, 0.3),
        "gemini-1.5-pro": (1.25, 5.0),
        "gemini-2.0-flash": (0.1, 0.4),
    }

    def __init__(self) -> None:
        self.session_metrics: List[Dict[str, Any]] = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int) -> None:
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(provider, model, usage),
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, provider: str, model: str, usage: Dict[str, int]) -> float:
        if provider == "local":
            return 0.0
        pt = usage.get("prompt_tokens", 0) / 1_000_000
        ct = usage.get("completion_tokens", 0) / 1_000_000
        key = model.lower()
        for name, (ip, op) in self._RATES_PER_M.items():
            if name in key:
                return round(pt * ip + ct * op, 6)
        return round((usage.get("total_tokens", 0) / 1000) * 0.01, 6)

    def summarize_session(self) -> Dict[str, Any]:
        if not self.session_metrics:
            return {"requests": 0}
        lat = [int(m["latency_ms"]) for m in self.session_metrics]
        lat_sorted = sorted(lat)
        mid = lat_sorted[len(lat_sorted) // 2]
        return {
            "requests": len(self.session_metrics),
            "total_tokens": sum(int(m["total_tokens"]) for m in self.session_metrics),
            "total_cost_estimate_usd": round(sum(float(m["cost_estimate"]) for m in self.session_metrics), 6),
            "latency_ms_p50": mid,
            "latency_ms_p99": lat_sorted[int(0.99 * (len(lat_sorted) - 1))] if lat_sorted else 0,
            "latency_ms_max": max(lat_sorted),
        }

    def reset(self) -> None:
        self.session_metrics.clear()


tracker = PerformanceTracker()
