import asyncio
import logging
import os

# --- Import all the components ---
from trading_bot.data_ingestion import DataIngestor
from trading_bot.event_engine import EventEngine
from trading_bot.strategy import LoggingStrategy
from trading_bot.oms import OrderManagementSystem

def setup_logging():
    """Sets up a more sophisticated root logger for the application."""
    log_file = 'trading_bot.log'
    if os.path.exists(log_file):
        os.remove(log_file)

    # Get the root logger
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)  # Set root logger to the lowest level

    # Create a file handler which logs even debug messages
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    # Create a console handler with a higher log level for cleaner console output
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)-25s - %(levelname)-8s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # Set third-party loggers to a higher level to reduce noise
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.info("Logging configured with DEBUG level for file and INFO level for console.")

async def main():
    """
    The main function to initialize and run the trading bot.
    This function orchestrates the entire application.
    """
    logging.info("--- Trading Bot Application Starting ---")

    # 1. Initialize all the main components of the system
    event_engine = EventEngine()
    data_ingestor = DataIngestor()
    strategy = LoggingStrategy()
    oms = OrderManagementSystem() # The strategy will need a reference to this if it places orders

    # 2. Wire the components together. This is the core of the setup.
    # The EventEngine needs to know which methods to call for each event type.
    # Here, we tell it that for every 'QuoteEvent', it should call the 'on_quote' method of our strategy instance.
    event_engine.register_handler('QuoteEvent', strategy.on_quote)

    # In a real strategy, we would pass the OMS to the strategy so it can execute orders.
    # e.g., setattr(strategy, 'oms', oms)

    # 3. Create and run the main concurrent tasks
    # We need to run the data ingestor (which produces events) and the event engine
    # (which consumes and dispatches events) concurrently.
    ingestor_task = asyncio.create_task(data_ingestor.start_streaming())
    engine_task = asyncio.create_task(event_engine.run())

    # The application will run until one of the tasks finishes or is cancelled.
    # In this case, they run indefinitely until the program is stopped.
    logging.info("All components initialized and tasks started. The bot is now live.")
    await asyncio.gather(ingestor_task, engine_task)

    logging.info("--- Trading Bot Application Shutting Down ---")


if __name__ == '__main__':
    setup_logging()
    try:
        # A pragmatic solution for the unstable environment: ensure dependencies are installed.
        # In a real deployment, this would be handled by a Dockerfile or setup script.
        print("Ensuring dependencies are installed...")
        os.system('pip install pyyaml websockets --quiet')
        print("Dependencies checked. Starting bot.")

        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Application stopped by user (Ctrl+C).")
    except Exception as e:
        logging.critical(f"A critical, unhandled error occurred at the top level: {e}", exc_info=True)
