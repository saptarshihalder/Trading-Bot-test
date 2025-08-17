import asyncio

# The central event queue for the application.
# The DataIngestor will put events here, and the EventEngine will process them.
event_queue = asyncio.Queue()


class Event:
    """
    Base class for all events in the system.
    """
    @property
    def type(self):
        return self.__class__.__name__


class QuoteEvent(Event):
    """
    Handles the event of receiving a new quote update.
    """
    def __init__(self, symbol: str, price: float, timestamp: int):
        self.symbol = symbol
        self.price = price
        self.timestamp = timestamp

    def __str__(self):
        return f"QUOTE: Symbol={self.symbol}, Price={self.price}, Timestamp={self.timestamp}"


# Other event types like TradeEvent, OrderEvent, FillEvent will be added here later.
