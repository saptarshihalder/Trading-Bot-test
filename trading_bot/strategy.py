import logging
from trading_bot.event import QuoteEvent

logger = logging.getLogger(__name__)

class Strategy:
    """
    The base class for all trading strategies.

    Strategies define how to react to market events. This class provides the
    interface that the EventEngine will use to pass events to the strategy.
    """
    def __init__(self):
        logger.info(f"Strategy '{self.__class__.__name__}' initialized.")

    async def on_quote(self, event: QuoteEvent):
        """
        This method is called by the EventEngine when a QuoteEvent is received.

        Subclasses should implement their trading logic in this method.
        """
        # Base strategy does nothing with the event.
        pass

    # In the future, we could add more event handlers, for example:
    # async def on_trade(self, event: TradeEvent):
    #     pass
    #
    # async def on_order_status_update(self, event: OrderUpdateEvent):
    #     pass


class LoggingStrategy(Strategy):
    """
    A simple example strategy that just logs the events it receives.

    This is useful for debugging and verifying that the event pipeline is working
    from the data source all the way to the strategy.
    """
    def __init__(self):
        super().__init__()

    async def on_quote(self, event: QuoteEvent):
        """
        Logs the details of the quote event to the console/log file.
        """
        logger.info(f"--> LoggingStrategy received quote: {event}")
        # In a real strategy, you might do something like:
        # if event.price > self.some_threshold:
        #     self.place_buy_order(event.symbol, 100)
        # For now, we just log to prove the data is flowing.
