import logging


def configure_logging() -> None:
    """Configure predictable, structured key-value logs for the API process."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s level=%(levelname)s logger=%(name)s message=%(message)s",
    )
