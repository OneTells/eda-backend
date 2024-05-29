from core.modules.logger.methods import add_logger_handlers
from core.modules.logger.objects import logger


def enable_logger() -> None:
    logger.enable('utils')

    logger.remove()
    add_logger_handlers("/root/scans/memory/logs", None, -1002036324115)
