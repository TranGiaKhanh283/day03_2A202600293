from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, List


def _ensure_logs_dir(log_dir: str = "logs") -> str:
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def append_experiment_record(record: Dict[str, Any], log_dir: str = "logs") -> None:
    """
    Append one structured experiment record for later analysis.
    Output file: logs/experiments.jsonl
    """
    d = _ensure_logs_dir(log_dir)
    path = os.path.join(d, "experiments.jsonl")
    payload = {"timestamp": datetime.utcnow().isoformat(), **record}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_compare_csv(row: Dict[str, Any], log_dir: str = "logs") -> None:
    """
    Append one comparison row to a CSV that can be opened directly in Excel/Sheets.
    Output file: logs/compare_summary.csv
    """
    d = _ensure_logs_dir(log_dir)
    path = os.path.join(d, "compare_summary.csv")

    ordered_cols: List[str] = [
        "timestamp",
        "scenario",
        "provider",
        "prompt_version",
        "question",
        "chatbot_requests",
        "chatbot_tokens",
        "chatbot_cost_usd",
        "chatbot_latency_p50_ms",
        "chatbot_latency_p99_ms",
        "agent_requests",
        "agent_tokens",
        "agent_cost_usd",
        "agent_latency_p50_ms",
        "agent_latency_p99_ms",
        "agent_v1_requests",
        "agent_v1_tokens",
        "agent_v1_cost_usd",
        "agent_v1_latency_p50_ms",
        "agent_v1_latency_p99_ms",
        "agent_v2_requests",
        "agent_v2_tokens",
        "agent_v2_cost_usd",
        "agent_v2_latency_p50_ms",
        "agent_v2_latency_p99_ms",
    ]

    csv_row = {k: row.get(k, "") for k in ordered_cols}
    csv_row["timestamp"] = datetime.utcnow().isoformat()

    file_exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ordered_cols)
        if not file_exists:
            writer.writeheader()
        writer.writerow(csv_row)
