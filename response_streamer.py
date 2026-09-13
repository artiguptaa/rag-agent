import asyncio
from collections.abc import AsyncIterator, Iterator
from typing import Any


class AsyncResponseStreamer:
    """Convert LlamaIndex synchronous streaming into async streaming."""

    async def stream(self, query_engine: Any, prompt: str) -> AsyncIterator[str]:
        response = await asyncio.to_thread(query_engine.query, prompt)

        if not hasattr(response, "response_gen"):
            yield str(response)
            return

        response_iterator: Iterator[str] = iter(response.response_gen)
        end_marker = object()

        while True:
            chunk = await asyncio.to_thread(
                next,
                response_iterator,
                end_marker,
            )

            if chunk is end_marker:
                break

            if chunk:
                yield str(chunk)