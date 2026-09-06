from __future__ import annotations

from typing import Any

from app.integrations.aws.clients import AWSClientFactory


class EventBridgeService:
    def __init__(self):
        self.client = AWSClientFactory.create_client("events")

    async def put_events(self, entries: list[dict[str, Any]]) -> None:
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.put_events(Entries=entries),
        )

    async def put_rule(self, name: str, schedule_expression: str) -> None:
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.put_rule(Name=name, ScheduleExpression=schedule_expression),
        )
