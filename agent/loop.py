"""minimal tool-loop skeleton.

no llm calls happen here. the caller injects model_fn, which looks at the
current AgentState and returns either a ToolCall or a FinalAnswer. tests pass a
stub, real models get wired in later weeks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Protocol, Sequence, Union, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """anything with a name and a __call__ that takes keyword args."""

    name: str

    def __call__(self, **kwargs: Any) -> Any: ...


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any] = field(default_factory=dict)
    tokens: int = 0


@dataclass
class FinalAnswer:
    answer: str | None
    tokens: int = 0


ModelOutput = Union[ToolCall, FinalAnswer]
ModelFn = Callable[["AgentState"], ModelOutput]


@dataclass
class AgentState:
    messages: list[dict[str, Any]] = field(default_factory=list)
    steps: int = 0
    tokens_used: int = 0


@dataclass
class AgentResult:
    answer: str | None
    trace: list[dict[str, Any]]
    state: AgentState
    stopped_reason: str  # "final_answer" or "max_steps"


def _index_tools(tools: Sequence[Tool] | Mapping[str, Tool]) -> dict[str, Tool]:
    if isinstance(tools, Mapping):
        return dict(tools)
    return {tool.name: tool for tool in tools}


def run_agent(
    question: str,
    tools: Sequence[Tool] | Mapping[str, Tool],
    model_fn: ModelFn,
    max_steps: int = 8,
) -> AgentResult:
    """run the loop until model_fn returns a FinalAnswer or max_steps is hit.

    every model step is one entry in the trace. tool errors (unknown tool or an
    exception inside the tool) are recorded in the trace and fed back to the
    model as a tool message instead of crashing the run.
    """
    by_name = _index_tools(tools)
    state = AgentState(messages=[{"role": "user", "content": question}])
    trace: list[dict[str, Any]] = []

    while state.steps < max_steps:
        output = model_fn(state)
        state.steps += 1
        state.tokens_used += getattr(output, "tokens", 0) or 0

        if isinstance(output, FinalAnswer):
            state.messages.append({"role": "assistant", "content": output.answer})
            trace.append({"step": state.steps, "type": "final_answer", "answer": output.answer})
            return AgentResult(output.answer, trace, state, "final_answer")

        if not isinstance(output, ToolCall):
            raise TypeError(f"model_fn must return ToolCall or FinalAnswer, got {type(output).__name__}")

        entry: dict[str, Any] = {
            "step": state.steps,
            "type": "tool_call",
            "tool": output.name,
            "args": dict(output.args),
        }
        tool = by_name.get(output.name)
        if tool is None:
            entry["error"] = f"unknown tool: {output.name}"
        else:
            try:
                entry["result"] = tool(**output.args)
            except Exception as exc:  # recorded, not raised: failures are data
                entry["error"] = f"{type(exc).__name__}: {exc}"

        state.messages.append(
            {"role": "assistant", "tool_call": {"name": output.name, "args": dict(output.args)}}
        )
        state.messages.append(
            {
                "role": "tool",
                "name": output.name,
                "content": entry.get("result"),
                "error": entry.get("error"),
            }
        )
        trace.append(entry)

    return AgentResult(None, trace, state, "max_steps")
