import logging
from trading_bot.strategy import Strategy
from trading_bot.event import QuoteEvent
from trading_bot.oms import OrderManagementSystem

logger = logging.getLogger(__name__)

class SimpleBuyStrategy(Strategy):
    """
    A simple strategy designed to test the Order Management System.

    It places a single market buy order for a small quantity of a stock
    as soon as it receives the first quote event.
    """
    def __init__(self, oms: OrderManagementSystem):
        super().__init__()
        if oms is None:
            raise ValueError("OrderManagementSystem cannot be None.")
        self.oms = oms
        self.has_traded = False # A flag to ensure we only trade once

    async def on_quote(self, event: QuoteEvent):
        """
        On receiving a quote, if we haven't traded yet, place a buy order.
        """
        if not self.has_traded:
            logger.info(f"SimpleBuyStrategy received its first quote for {event.symbol}, placing a buy order.")
            try:
                # Place a market order to buy 1 share
                await self.oms.execute_order(
                    symbol=event.symbol,
                    qty=1,
                    side='buy',
                    order_type='market'
                )
                self.has_traded = True # Set flag to prevent more trades
                logger.info(f"SimpleBuyStrategy has placed its one-time order for {event.symbol}.")
            except Exception:
                logger.exception(f"SimpleBuyStrategy failed to place an order for {event.symbol}.")
