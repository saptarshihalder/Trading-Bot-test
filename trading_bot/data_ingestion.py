import asyncio
import json
import yaml
import websockets
import os
import logging
from trading_bot.event import event_queue, QuoteEvent

# Get a logger instance (it's configured in the main script, but we can get it here)
logger = logging.getLogger(__name__)


class DataIngestor:
    """
    Connects to a WebSocket feed, parses data, and puts events onto a queue.
    """
    def __init__(self, config_path='config/config.yml'):
        logger.info("Initializing DataIngestor.")
        try:
            self._config = self._load_config(config_path)
            # This is a bit rigid, a factory pattern would be better for multiple sources
            self._api_key = os.environ.get('TWELVEDATA_API_KEY')
            if not self._api_key:
                raise ValueError("TWELVEDATA_API_KEY environment variable not set")
            self._base_url = self._config['twelvedata']['stream_url']
            self._symbol = self._config['trading']['symbol']
            self._stream_url = self._base_url
            self._headers = {'Authorization': f'Bearer {self._api_key}'}
            logger.info("Configuration loaded for Twelve Data.")
            logger.debug(f"Stream URL: {self._base_url}")
        except Exception:
            logger.exception("Failed to initialize DataIngestor. Check config file.")
            raise

    def _load_config(self, path):
        logger.debug(f"Loading config from path: {path}")
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    async def start_streaming(self):
        """
        Connects to the Twelve Data WebSocket and puts events onto the queue.
        """
        logger.info("DataIngestor starting connection...")
        try:
            async with websockets.connect(self._stream_url, extra_headers=self._headers) as websocket:
                logger.info("WebSocket connection established.")
                subscribe_message = {
                    "action": "subscribe",
                    "params": {"symbols": self._symbol}
                }
                await websocket.send(json.dumps(subscribe_message))
                logger.info(f"Subscription message sent: {subscribe_message}")

                while True:
                    message = await websocket.recv()
                    logger.debug(f"Received raw message: {message}")
                    data = json.loads(message)

                    if data.get("event") == "subscribe-status":
                        logger.info(f"Subscription status received: {data}")
                        continue
                    if data.get("event") == "heartbeat":
                        logger.debug("Heartbeat received.")
                        continue

                    if data.get("event") == "price":
                        try:
                            event = QuoteEvent(
                                symbol=data['symbol'],
                                price=float(data['price']),
                                timestamp=int(data['timestamp'])
                            )
                            await event_queue.put(event)
                            logger.debug(f"Queued event: {event}")
                        except (KeyError, ValueError) as e:
                            logger.error(f"Could not parse price data into QuoteEvent: {data}. Error: {e}")
                    else:
                        logger.warning(f"Received unknown event type: {data}")

        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"Connection closed: Code={e.code}, Reason='{e.reason}'")
        except Exception:
            logger.exception("An unhandled error occurred in DataIngestor.")

# Standalone testing block
if __name__ == '__main__':
    # This setup is duplicated from the previous version for standalone testing
    log_file_main = 'debug_ingestor_test.log'
    if os.path.exists(log_file_main):
        os.remove(log_file_main)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_file_main), logging.StreamHandler()])

    logger.info("--- Data Ingestion Script Started in Standalone Mode ---")

    async def consume_events():
        """A simple consumer for testing purposes."""
        logger.info("Test event consumer started, waiting for events...")
        while True:
            event = await event_queue.get()
            print(f"\n>>> Consumed event from queue: {event}\n")
            event_queue.task_done()

    async def main():
        ingestor = DataIngestor()
        ingestor_task = asyncio.create_task(ingestor.start_streaming())
        consumer_task = asyncio.create_task(consume_events())
        await asyncio.gather(ingestor_task, consumer_task)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Standalone test stopped by user.")
    except Exception:
        logger.exception("A critical error occurred during standalone test.")
    logger.info("--- Data Ingestion Script Finished ---")
