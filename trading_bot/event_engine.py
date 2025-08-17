import asyncio
from collections import defaultdict
import logging
from trading_bot.event import event_queue

logger = logging.getLogger(__name__)

class EventEngine:
    """
    The core event engine of the trading bot.

    It pulls events from the central queue and dispatches them to registered handlers.
    This architecture decouples the data source from the strategy logic.
    """
    def __init__(self):
        logger.info("Initializing EventEngine.")
        # A dictionary where keys are event types (e.g., 'QuoteEvent')
        # and values are lists of callable handlers.
        self._handlers = defaultdict(list)

    def register_handler(self, event_type_name: str, handler):
        """
        Register a handler for a specific event type.

        Args:
            event_type_name: The string name of the event class (e.g., 'QuoteEvent').
            handler: A callable (function or method) that will be called with the event object.
        """
        self._handlers[event_type_name].append(handler)
        logger.info(f"Handler '{getattr(handler, '__name__', 'unknown')}' registered for event type '{event_type_name}'")

    async def run(self):
        """
        The main event loop.

        Pulls events from the queue and dispatches them to all registered handlers.
        """
        logger.info("Event engine is running and waiting for events...")
        while True:
            try:
                event = await event_queue.get()
                logger.debug(f"EventEngine dequeued event: {event}")

                if event.type in self._handlers:
                    for handler in self._handlers[event.type]:
                        # Run the handler as a non-blocking background task.
                        # This prevents a slow strategy from blocking the entire event loop.
                        asyncio.create_task(handler(event))

                event_queue.task_done()
            except Exception:
                logger.exception("An error occurred in the event engine's main loop.")
