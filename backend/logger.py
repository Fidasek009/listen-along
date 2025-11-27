"""Logging configuration."""

import logging

LOG_FILE = "backend.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=LOG_FILE,
)

log = logging.getLogger(__name__)
