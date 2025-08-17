import logging

logger = logging.getLogger(__name__)

class OrderManagementSystem:
    """
    A placeholder for the Order Management System (OMS).

    In a real trading bot, this component would be responsible for:
    - Managing the lifecycle of orders (sending, cancelling, updating).
    - Tracking order status (pending, filled, cancelled).
    - Communicating with the brokerage's API.

    For now, this is a mock implementation that just logs any orders it's
    asked to execute.
    """
    def __init__(self):
        logger.info("Initializing OrderManagementSystem (Mock).")

    async def execute_order(self, symbol: str, quantity: float, order_type: str = "MARKET"):
        """
        Receives an order from a strategy and 'executes' it by logging it.
        This is a simplified, direct-call method for now. A more advanced
        system would use OrderEvents and a dedicated order execution queue.

        Args:
            symbol: The symbol to trade (e.g., 'AAPL').
            quantity: The amount to trade. Positive for buy, negative for sell.
            order_type: The type of order (e.g., 'MARKET', 'LIMIT').
        """
        # In a real system, this would generate an OrderEvent and send it to the brokerage.
        # For now, we just log the action to show it was called.
        logger.info(
            f"--> OMS received order to execute: "
            f"Type={order_type}, Symbol={symbol}, Quantity={quantity}"
        )

        # We can also print to the console for more obvious feedback during testing.
        print(
            f"--- MOCK OMS: Pretending to execute {order_type} order "
            f"for {quantity} of {symbol} ---"
        )

        # A real OMS would return a unique order ID for tracking.
        return "mock_order_id_12345"
