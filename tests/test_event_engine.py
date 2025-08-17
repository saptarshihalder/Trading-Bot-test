import unittest
import asyncio
import logging
from trading_bot.event import event_queue, QuoteEvent
from trading_bot.event_engine import EventEngine

# Disable logging for tests to keep output clean, unless debugging
logging.disable(logging.CRITICAL)

class TestEventEngine(unittest.TestCase):

    def setUp(self):
        """Set up a new event loop and clear the queue for each test."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Clear the queue
        while not event_queue.empty():
            event_queue.get_nowait()

        self.engine = EventEngine()
        self.mock_handler_called = False
        self.received_event = None

    async def mock_handler(self, event):
        """A mock handler to test if the dispatcher calls it."""
        self.mock_handler_called = True
        self.received_event = event

    def test_register_and_dispatch(self):
        """
        Tests if the EventEngine can register a handler and dispatch an event to it.
        """
        async def run_test():
            # Create a sample event
            test_event = QuoteEvent(symbol="TEST", price=100.0, timestamp=12345)

            # Register the mock handler for 'QuoteEvent'
            self.engine.register_handler('QuoteEvent', self.mock_handler)

            # Start the engine in the background
            engine_task = asyncio.create_task(self.engine.run())

            # Put the test event onto the queue
            await event_queue.put(test_event)

            # Give the engine a moment to process the event
            await asyncio.sleep(0.01)

            # Assert that the handler was called and received the correct event
            self.assertTrue(self.mock_handler_called, "The mock handler was not called.")
            self.assertIsNotNone(self.received_event, "Handler did not receive an event.")
            self.assertEqual(self.received_event.symbol, "TEST")
            self.assertEqual(self.received_event.price, 100.0)

            # Cancel the engine task to clean up
            engine_task.cancel()
            try:
                await engine_task
            except asyncio.CancelledError:
                pass # Expected

        # Run the async test within the event loop
        self.loop.run_until_complete(run_test())

    def tearDown(self):
        """Close the event loop."""
        self.loop.close()

if __name__ == '__main__':
    unittest.main()
