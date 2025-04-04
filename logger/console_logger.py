import logging
import sys

def setup_logger(name='news_approval', log_level=logging.INFO):
    """
    Set up and configure console logger

    Args:
        name (str): Logger name
        log_level (int): Logging level

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define format for AWS CloudWatch readability
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Direct logs specifically to stdout for container environments
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = setup_logger()
