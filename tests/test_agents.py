import asyncio
import pytest
from unittest.mock import MagicMock
from pydantic import BaseModel
from typing import Optional
from any2json_py.utils.cost_tracker import CostTracker
from any2json_py.agents.coordinator import run_coordinator


class SimpleModel(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None


def _make_completion(prompt=10, completion=5):
    m = MagicMock()
    m.usage.prompt_tokens = prompt
    m.usage.completion_tokens = completion
    return m


def test_coordinator_merges(mocker):
    expected = SimpleModel(name="Alice", age="30")
    mocker.patch(
        "any2json_py.agents.coordinator.instructor.from_openai",
        return_value=MagicMock(
            chat=MagicMock(
                completions=MagicMock(
                    create_with_completion=MagicMock(return_value=(expected, _make_completion()))
                )
            )
        ),
    )
    mocker.patch("any2json_py.agents.coordinator.OpenAI")

    tracker = CostTracker()
    partials = [SimpleModel(name="Alice"), SimpleModel(age="30")]
    result = run_coordinator(partials, SimpleModel, tracker)
    assert result.name == "Alice"
    assert tracker.total_prompt_tokens == 10


@pytest.mark.asyncio
async def test_worker_runs(mocker):
    from any2json_py.agents.worker import run_worker
    expected = SimpleModel(name="Bob")
    mocker.patch(
        "any2json_py.agents.worker.instructor.from_openai",
        return_value=MagicMock(
            chat=MagicMock(
                completions=MagicMock(
                    create_with_completion=MagicMock(return_value=(expected, _make_completion()))
                )
            )
        ),
    )
    mocker.patch("any2json_py.agents.worker.OpenAI")

    tracker = CostTracker()
    result = await run_worker("Bob is a developer.", SimpleModel, tracker)
    assert result.name == "Bob"
