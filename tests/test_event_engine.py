import asyncio
import contextlib
import logging

from trading_bot.event import event_queue, QuoteEvent
from trading_bot.event_engine import EventEngine

# Disable logging during tests
logging.disable(logging.CRITICAL)


def clear_queue():
    while not event_queue.empty():
        event_queue.get_nowait()
        event_queue.task_done()


def test_register_and_dispatch():
    async def run_test():
        clear_queue()
        engine = EventEngine()
        called = False
        received = None

        async def handler(event):
            nonlocal called, received
            called = True
            received = event

        engine.register_handler("QuoteEvent", handler)
        engine_task = asyncio.create_task(engine.run())
        await event_queue.put(QuoteEvent("TEST", 100.0, 12345))
        await asyncio.sleep(0.01)
        assert called
        assert received.symbol == "TEST"
        assert received.price == 100.0
        engine_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await engine_task

    asyncio.run(run_test())


def test_sync_handler_support():
    async def run_test():
        clear_queue()
        engine = EventEngine()
        results = {"called": False, "event": None}

        def sync_handler(event):
            results["called"] = True
            results["event"] = event

        engine.register_handler("QuoteEvent", sync_handler)
        engine_task = asyncio.create_task(engine.run())
        await event_queue.put(QuoteEvent("SYNC", 1.0, 1))
        await asyncio.sleep(0.01)
        assert results["called"]
        assert results["event"].symbol == "SYNC"
        engine_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await engine_task

    asyncio.run(run_test())
