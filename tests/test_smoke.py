import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_imports():
    import agent
    import evals
    import evals.gold
    import evals.metrics
    import evals.run_eval
    import retrieval

    assert agent.run_agent is not None
    assert retrieval.__doc__


def test_recall_at_k():
    from evals.metrics import recall_at_k

    assert recall_at_k(["a", "b", "c"], ["a"], k=1) == 1.0
    assert recall_at_k(["a", "b", "c"], ["c"], k=2) == 0.0
    assert recall_at_k(["a", "b", "c"], ["a", "c"], k=2) == 0.5
    assert recall_at_k(["a", "b", "c"], ["a", "c"], k=5) == 1.0
    assert recall_at_k(["a"], [], k=5) == 0.0
    with pytest.raises(ValueError):
        recall_at_k(["a"], ["a"], k=0)


def test_reciprocal_rank_and_mean():
    from evals.metrics import mean, reciprocal_rank

    assert reciprocal_rank(["a", "b", "c"], ["a"]) == 1.0
    assert reciprocal_rank(["a", "b", "c"], ["c", "b"]) == 0.5
    assert reciprocal_rank(["a", "b"], ["z"]) == 0.0
    assert mean([1.0, 0.5, 0.0]) == 0.5
    assert mean([]) is None


class EchoSearch:
    name = "search"

    def __init__(self):
        self.calls = []

    def __call__(self, query):
        self.calls.append(query)
        return [f"doc-for-{query}"]


def test_run_agent_one_tool_call_then_answer():
    from agent.loop import AgentState, FinalAnswer, ToolCall, run_agent

    def model_fn(state: AgentState):
        if state.steps == 0:
            return ToolCall("search", {"query": "rate limits"}, tokens=10)
        last = state.messages[-1]
        assert last["role"] == "tool"
        return FinalAnswer(f"found {last['content'][0]}", tokens=5)

    search = EchoSearch()
    result = run_agent("what are the rate limits?", [search], model_fn)

    assert result.answer == "found doc-for-rate limits"
    assert result.stopped_reason == "final_answer"
    assert search.calls == ["rate limits"]
    assert result.trace == [
        {
            "step": 1,
            "type": "tool_call",
            "tool": "search",
            "args": {"query": "rate limits"},
            "result": ["doc-for-rate limits"],
        },
        {"step": 2, "type": "final_answer", "answer": "found doc-for-rate limits"},
    ]
    assert result.state.steps == 2
    assert result.state.tokens_used == 15


def test_run_agent_stops_at_max_steps_and_records_tool_errors():
    from agent.loop import ToolCall, run_agent

    result = run_agent("q", [], lambda state: ToolCall("missing"), max_steps=3)
    assert result.answer is None
    assert result.stopped_reason == "max_steps"
    assert len(result.trace) == 3
    assert all(e["error"] == "unknown tool: missing" for e in result.trace)


def test_run_eval_stub_on_empty_gold(tmp_path, capsys):
    from evals.run_eval import main

    gold = tmp_path / "gold.jsonl"
    gold.write_text("")
    out = tmp_path / "runs" / "latest-stub.json"

    assert main(["--gold", str(gold), "--out", str(out)]) == 0
    assert "0 questions, nothing to score" in capsys.readouterr().out
    assert json.loads(out.read_text()) == {
        "status": "stub",
        "n_questions": 0,
        "metrics": {
            "recall_at_5": None,
            "mrr": None,
            "answer_correctness": None,
            "refusal_rate": None,
            "cost_usd": None,
            "latency_p50_s": None,
        },
    }


def test_repo_gold_file_is_empty_and_loads():
    from evals.gold import load_gold

    gold = REPO_ROOT / "questions" / "gold.jsonl"
    assert gold.stat().st_size == 0
    assert load_gold(gold) == []


def test_run_eval_with_questions_but_no_retriever(tmp_path, capsys):
    from evals.run_eval import run

    gold = tmp_path / "gold.jsonl"
    lines = [
        {
            "id": "q001",
            "question": "what is the default max_tokens?",
            "answerable": True,
            "gold_answer": "1024",
            "gold_passages": [{"doc_id": "d1", "start_char": 0, "end_char": 4, "text": "1024"}],
            "tags": ["lookup"],
        },
        {
            "id": "q002",
            "question": "what is the ceo's favourite colour?",
            "answerable": False,
            "gold_answer": None,
            "gold_passages": [],
            "tags": ["unanswerable"],
        },
    ]
    gold.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    result = run(gold, tmp_path / "out.json")
    assert result["n_questions"] == 2
    assert result["status"] == "stub"
    assert all(v is None for v in result["metrics"].values())
    assert "no retriever is wired" in capsys.readouterr().out


@pytest.mark.parametrize(
    "bad",
    [
        {"id": "q1", "question": "x", "answerable": False, "gold_answer": "y", "gold_passages": [], "tags": []},
        {"id": "x1", "question": "x", "answerable": False, "gold_answer": None, "gold_passages": [], "tags": []},
        {"id": "q1", "question": "x", "answerable": True, "gold_answer": "y", "gold_passages": [], "tags": []},
        {"id": "q1", "question": "x", "answerable": False, "gold_answer": None, "gold_passages": []},
    ],
)
def test_invalid_gold_lines_are_rejected(tmp_path, bad):
    from evals.gold import GoldValidationError, load_gold
    from evals.run_eval import main

    gold = tmp_path / "gold.jsonl"
    gold.write_text(json.dumps(bad) + "\n")
    with pytest.raises(GoldValidationError):
        load_gold(gold)
    assert main(["--gold", str(gold), "--out", str(tmp_path / "o.json")]) == 1


def test_schema_json_matches_validator_keys():
    schema = json.loads((REPO_ROOT / "questions" / "schema.json").read_text())
    from evals.gold import _PASSAGE_KEYS, _TOP_KEYS

    assert set(schema["required"]) == _TOP_KEYS
    assert set(schema["properties"]["gold_passages"]["items"]["required"]) == _PASSAGE_KEYS


def test_module_entrypoint_runs(tmp_path):
    gold = tmp_path / "gold.jsonl"
    gold.write_text("")
    out = tmp_path / "stub.json"
    proc = subprocess.run(
        [sys.executable, "-m", "evals.run_eval", "--gold", str(gold), "--out", str(out)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert json.loads(out.read_text())["status"] == "stub"
