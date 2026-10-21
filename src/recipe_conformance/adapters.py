# SPDX-License-Identifier: Apache-2.0
"""Adapters that execute a fixture under one chunk-split plan."""

from __future__ import annotations

import copy
import json
from typing import Any, Protocol

from .models import SplitPlan, StreamFixture


class StreamAdapter(Protocol):
    name: str

    def run(self, fixture: StreamFixture, plan: SplitPlan) -> list[Any]: ...


class OfficialPythonAdapter:
    """Adapter for the official `deepseek_recipe` Python bindings."""

    name = "deepseek-recipe-python"

    def __init__(self) -> None:
        try:
            import deepseek_recipe
        except ImportError as exc:  # pragma: no cover - depends on optional package
            raise RuntimeError("Install the optional 'official' dependencies to use this adapter") from exc
        self._recipe = deepseek_recipe

    def run(self, fixture: StreamFixture, plan: SplitPlan) -> list[Any]:
        recipe = self._recipe
        request_classes = {
            "chat_completions": recipe.ChatCompletionRequest,
            "responses": recipe.ResponsesRequest,
            "messages": recipe.MessagesRequest,
        }
        request_class = request_classes[fixture.protocol]
        request = request_class(copy.deepcopy(fixture.request))
        converted = request.convert(recipe.ConversionOptions())
        generator = request_class.chunk_generator(converted, f"conformance-{fixture.id}", fixture.model)
        processor = recipe.StreamProcessor(generator, converted.parsing_options)
        events: list[Any] = []
        events.extend(
            processor.push(
                recipe.InferenceChunk.ready(
                    prompt_usage=recipe.PromptUsage(
                        prompt_tokens=fixture.prompt_tokens,
                        prompt_cache_hit_tokens=fixture.prompt_cache_hit_tokens,
                    ),
                    system_fingerprint="conformance",
                )
            )
        )
        for piece in plan.pieces:
            events.extend(processor.push(recipe.InferenceChunk.text(piece, token_count=len(piece))))
        finish_reason = getattr(recipe.InferenceFinishReason, fixture.finish_reason)
        events.extend(processor.push(recipe.InferenceChunk.finish(finish_reason)))
        events.extend(processor.finish())
        return [_event_to_json(event) for event in events]


def _event_to_json(event: Any) -> Any:
    if hasattr(event, "to_json"):
        value = event.to_json()
        return json.loads(value) if isinstance(value, str) else value
    if isinstance(event, dict):
        return event
    raise TypeError(f"adapter returned unsupported event type: {type(event).__name__}")


class JoinedTextMockAdapter:
    """Test adapter that emits one final text event independent of source chunking."""

    name = "joined-text-mock"

    def run(self, fixture: StreamFixture, plan: SplitPlan) -> list[Any]:
        return [{"kind": "text", "content": "".join(plan.pieces)}]


class ChunkEchoMockAdapter:
    """Test adapter that incorrectly exposes source chunk boundaries in output."""

    name = "chunk-echo-mock"

    def run(self, fixture: StreamFixture, plan: SplitPlan) -> list[Any]:
        return [{"kind": "text", "content": piece} for piece in plan.pieces]
