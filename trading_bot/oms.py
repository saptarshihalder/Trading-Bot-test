import logging
import yaml
import alpaca_trade_api as tradeapi
import os

logger = logging.getLogger(__name__)

class OrderManagementSystem:
    """
    The Order Management System (OMS) for connecting to Alpaca.

    This component is responsible for executing trades via the Alpaca API.
    """
    def __init__(self, config_path='config/config.yml'):
        logger.info("Initializing OrderManagementSystem for Alpaca.")
        try:
            self._config = self._load_config(config_path)
            alpaca_config = self._config['alpaca']

            key_id = os.environ.get('ALPACA_KEY_ID')
            secret_key = os.environ.get('ALPACA_SECRET_KEY')
            if not key_id or not secret_key:
                raise ValueError("ALPACA_KEY_ID and ALPACA_SECRET_KEY environment variables must be set")

            self.api = tradeapi.REST(
                key_id=key_id,
                secret_key=secret_key,
                base_url=alpaca_config['base_url'],
                api_version='v2'
            )
            # Verify the connection by fetching account information
            account = self.api.get_account()
            logger.info(f"Successfully connected to Alpaca. Account Status: {account.status}")
            logger.info(f"Paper Trading Account: {account.paper_trading}")

        except Exception as e:
            logger.exception("Failed to initialize Alpaca OMS. Check API keys and config.")
            # Re-raise the exception to halt initialization if OMS fails
            raise e

    def _load_config(self, path):
        """Loads the YAML configuration file."""
        logger.debug(f"Loading config from path: {path}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found at {path}")
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    async def execute_order(self, symbol: str, qty: float, side: str, order_type: str = 'market', time_in_force: str = 'day'):
        """
        Submits an order to the Alpaca API.

        Args:
            symbol (str): The symbol to trade.
            qty (float): The number of shares to trade. Must be positive.
            side (str): 'buy' or 'sell'.
            order_type (str): 'market', 'limit', 'stop', etc.
            time_in_force (str): 'day', 'gtc', 'opg', etc.

        Returns:
            The order object from Alpaca if successful, otherwise None.
        """
        logger.info(f"Submitting {side} order for {qty} shares of {symbol} to Alpaca.")
        try:
            # Alpaca API expects qty to be a positive number.
            order = self.api.submit_order(
                symbol=symbol,
                qty=abs(float(qty)),
                side=side,
                type=order_type,
                time_in_force=time_in_force
            )
            logger.info(f"Successfully submitted order to Alpaca. Order ID: {order.id}, Status: {order.status}")
            print(f"--- REAL OMS: Submitted {side} order for {qty} of {symbol} to Alpaca. Order ID: {order.id} ---")
            return order
        except Exception:
            logger.exception(f"Failed to submit order for {symbol} to Alpaca.")
            return None
