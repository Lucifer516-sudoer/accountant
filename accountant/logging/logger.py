"""
This module contains logging-related things.
And Mainly a base logger that can be used to derive child loggers

Exposed Loggers:
    - `app_logger` -> Name: `accountant`
"""

import logging

from accountant.logging._custom_handler import (  # noqa: F401
    RichConsoleHandler,  # type: ignore
    RichFileHandler,  # type: ignore
)
from accountant.logging._log_file_creator import create_log_file  # noqa: F401

app_logger: logging.Logger = logging.getLogger("accountant")
# flet_logger: logging.Logger = logging.getLogger("flet")
# flet_core_logger: logging.Logger = logging.getLogger("flet_core")


def _configure_handler(logger: logging.Logger, handlers: list[logging.Handler]):
    """
    Just removes any default handler to the given logger and adds the given handlers to it.
    Never call this inside any script unless needed, bcoz removes all the already present logging handlers


    Args:
        logger (logging.Logger): The logger object to attach the handler with
        handlers (list[logging.Handler]): The list of handlers to attach to the logger
    """

    logger.handlers = []  # just makes the handler to be a none handler
    for each in handlers:
        if each not in logger.handlers:
            logger.addHandler(each)


def configure_present_loggers(
    loggers: list[logging.Logger], handlers: list[logging.Handler]
):
    """
    Just removes any default handler to the given set of loggers and adds the given handlers to it.
    Never call this inside any script unless needed, bcoz removes all the already present logging handlers


    Args:
        logger (list[logging.Logger]): The logger object to attach the handler with
        handler (list[logging.Handler]): The list of handlers to attach to the logger
    """
    for logger in loggers:
        _configure_handler(logger, handlers)
