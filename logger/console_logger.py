import logging
import sys

def setup_logger(name='news_approval', log_level=logging.INFO):
    """
    Set up and configure console logger optimized for Railway
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define format for better readability
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Direct logs to stdout with immediate flush
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    # Ensure immediate flush
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # Add an immediate log to verify logger works
    logger.info("Logger initialized")

    return logger

# Initialize logger
logger = setup_logger()
