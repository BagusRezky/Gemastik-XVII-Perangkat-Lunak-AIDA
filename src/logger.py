import logging
import os
import sys

def setup_logger():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Determine the number of the run
    run_number = 1
    while os.path.exists(f'logs/run_{run_number}.log'):
        run_number += 1

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/run_{run_number}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.run_number = run_number  # Add run_number attribute to logger
    return logger
