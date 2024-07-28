"""
This module contains logging-related things.
# And Mainly a base logger that can be used to derive child loggers
"""

import logging
from typing import TypeAlias

from accountant.logging.logger import (
    RichConsoleHandler,
    RichFileHandler,
    app_logger,
    configure_present_loggers,
    create_log_file,
    # flet_core_logger,
    # flet_logger,
)

Logger: TypeAlias = logging.Logger
__all__ = [
    "Logger",
    "app_logger",
    "RichConsoleHandler",
    "RichFileHandler",
    "configure_present_loggers",
    "logging",
    "create_log_file",
    # "flet_logger",
    # "flet_core_logger",
]
