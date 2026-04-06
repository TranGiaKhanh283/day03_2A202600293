# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: C4
- **Team Members**: Trần Gia Khánh - 2A202600293, Phạm Trần Thanh Lâm - 2A202600270, Phạm Việt Cường - 2A202600420, Nguyễn Lâm Tùng - 2A202600173, Đặng Tiến Dũng - 2A202600024, Phạm Hữu Hoàng Hiệp - 2A202600415

- **Deployment Date**: 2026-04-06

---

## 1. Executive Summary

This project compares a single-shot chatbot baseline against two ReAct agents (v1 and v2) for a multi-step travel planning task:

> "Tìm khách sạn ở Đà Lạt cuối tuần dưới 800k/đêm, kiểm tra thời tiết, và gợi ý trang phục phù hợp."

The baseline chatbot is intentionally tool-less. The agents use tools for weather, hotel search, and hotel review retrieval. We then analyze traces, parser/tool errors, and token/latency behavior to evaluate reliability.

- **Success Rate**: 0/1 strict success for this final multi-step Da Lat case (all systems failed strict correctness in different ways).
- **Key Outcome**: ReAct architecture enabled multi-step tool interaction, but with local Phi-3 the run still suffered hallucination/format instability. The logs clearly exposed failure modes (parse drift and ungrounded final answers), giving concrete directions for Agent v3+ improvements.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
Implemented loop in `src/agent/agent.py`:

1. Receive user query.
2. Generate model output under strict prompt (`Thought`, `Action`, `Final Answer`).
3. Parse `Action: tool_name(...)`.
4. Execute tool and append `Observation: ...` to the scratchpad.
5. Repeat until `Final Answer` or `max_steps`.
6. Log telemetry (`AGENT_START`, `TOOL_CALL`, `AGENT_ERROR`, `AGENT_END`, `LLM_METRIC`).

This follows the required Thought-Action-Observation pattern and feeds observations back into the next prompt cycle.

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `get_weather` | `json` or `key=value` | Return Da Lat weather snapshot for target date, used for clothing recommendation. |
| `search_hotels` | `json` or `key=value` | Return hotel candidates for city/check-in/check-out/budget filter. |
| `get_hotel_reviews` | `json` or `key=value` | Return rating and highlights for a selected hotel before final recommendation. |

### 2.3 LLM Providers Used
- **Primary (final measured run)**: Local Phi-3 (`Phi-3-mini-4k-instruct-q4.gguf` via `llama-cpp-python`)
- **Secondary (code-level support)**: OpenAI / Gemini provider interfaces were implemented in the provider factory, but the final scored Da Lat run in this report used Local provider.

---

## 3. Telemetry & Performance Dashboard

Metrics below are from the final command:

`python run_lab.py dalat-compare`

Scenario:
- "Tìm khách sạn ở Đà Lạt ... dưới 800000 VND/đêm ... kiểm tra thời tiết ... gợi ý trang phục."

Collected summary:
- Chatbot: 443 tokens, 1 request, latency 24603ms
- Agent v1: 3477 tokens, 2 requests, latencies 100304ms and 47580ms
- Agent v2: 3376 tokens, 2 requests, latencies 81699ms and 23596ms

- **Average Latency (P50)**: ~47580ms (across 5 LLM requests in this run)
- **Max Latency (P99)**: ~100304ms
- **Average Tokens per Task**: ~2432 tokens/task (`(443 + 3477 + 3376) / 3`)
- **Total Cost of Test Suite**: $0.00 (local model run)

---

## 4. Root Cause Analysis (RCA) - Failure Traces

*Deep dive into why the agent failed in the Da Lat test case.*

### Case Study A: Hallucinated Recommendation (Agent v1)
- **Input**: "Tìm khách sạn ở Đà Lạt ... dưới 800000 VND/đêm ..."
- **Observation**: Agent v1 ended with "Green Valley Inn (750,000 VND)" even though that hotel was not in tool inventory (`Ngọc Lan`, `Mimosa`, `Sapa Lodge`).
- **Root Cause**:
  - Prompt v1 was too permissive.
  - Final answer had no post-validation against observed tool outputs.
  - Local model tendency to hallucinate plausible entities.

### Case Study B: Parse Drift + Topic Drift (Agent v2)
- **Input**: same Da Lat scenario.
- **Observation**:
  - Log recorded `AGENT_ERROR` with `code: PARSE_ERROR` at step 0.
  - Final answer became unrelated narrative text ("fog-laden streets of London...").
- **Root Cause**:
  - Model failed strict format compliance despite stronger instructions.
  - Recovery message was insufficient to force deterministic structured output under local model constraints.
  - Long prompt context increased drift risk.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2
- **Diff**:
  - v1: minimal ReAct instruction, simple action examples.
  - v2: stricter guardrails, JSON-style action examples, explicit tool-order policy, stronger output constraints.
- **Result**:
  - v2 reduced flexibility but did not improve final correctness in this run due to model drift.
  - v2 produced explicit parser failure trace (`PARSE_ERROR`) which improved diagnosability.
  - v1 produced a plausible but ungrounded hallucination (harder to detect without trace checks).

### Experiment 2 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Da Lat multi-step planning | Refused specifics, gave generic tips (safe but not actionable) | Attempted tool-based reasoning but failed correctness (v1 hallucination, v2 drift) | **Draw (different failure modes)** |
| Architecture capability | No tool use by design | Supports multi-step tool orchestration | **Agent (architecture)** |

---

## 6. Production Readiness Review

*Considerations for taking this system to a real-world environment.*

- **Security**:
  - Sanitize and schema-validate tool arguments before execution.
  - Keep secrets only in `.env`, rotate any leaked key immediately, and enforce secret scanning in CI.
  - Redact sensitive fields in telemetry logs.
- **Guardrails**:
  - Add strict structured decoding / JSON mode where available.
  - Add final-answer grounding check (reject hotels not present in latest `search_hotels` observation).
  - Maintain retry budget, max steps, and parser fallback templates.
- **Scaling**:
  - Move tool execution to async queue workers.
  - Add evaluation harness with regression test suite for failure traces.
  - Introduce retrieval-based tool routing and eventually graph orchestration (LangGraph-style) for complex branching.

---

> [!NOTE]
> Final submission file should be renamed to `GROUP_REPORT_Dalat_ReAct_Team.md` in this folder.
