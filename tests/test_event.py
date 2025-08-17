import unittest
from trading_bot.event import QuoteEvent, Event

class TestEvent(unittest.TestCase):
    """
    Tests for the event classes.
    """

    def test_base_event_type(self):
        """Tests that the base Event class has a type property."""
        event = Event()
        self.assertEqual(event.type, 'Event')

    def test_quote_event_creation(self):
        """Tests that a QuoteEvent is created with the correct attributes."""
        event = QuoteEvent(symbol="AAPL", price=150.5, timestamp=1672531200)
        self.assertEqual(event.type, 'QuoteEvent')
        self.assertEqual(event.symbol, "AAPL")
        self.assertEqual(event.price, 150.5)
        self.assertEqual(event.timestamp, 1672531200)
        self.assertTrue(isinstance(event, Event))
        self.assertEqual(str(event), "QUOTE: Symbol=AAPL, Price=150.5, Timestamp=1672531200")

if __name__ == '__main__':
    unittest.main()
