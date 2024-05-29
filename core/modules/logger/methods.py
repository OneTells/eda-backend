import os
from sys import stderr

from loguru import logger

from core.modules.logger.handlers.telegram import Telegram


def add_logger_handlers(path: str, token: str | None, chat_id: int) -> None:
    logger.add(
        stderr, level="INFO",
        format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
        filter=lambda x: 'context' in x['extra'],
        backtrace=True, diagnose=True
    )

    if token is not None:
        logger.add(
            Telegram(token, chat_id), level='WARNING',
            filter=lambda x: 'context' in x['extra']
        )

    os.makedirs(path, exist_ok=True)

    logger.add(
        f'{path}/info.log', level='INFO',
        format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
        filter=lambda x: 'context' in x['extra'],
        backtrace=True, diagnose=True, enqueue=True,
        compression='tar.xz', retention='10 days', rotation='100 MB'
    )

    logger.add(
        f'{path}/debug.log', level='DEBUG',
        format="<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <y>{level}</> | <w>{extra[context]}</> | <c>{message}</>",
        filter=lambda x: 'context' in x['extra'],
        backtrace=True, diagnose=True, enqueue=True,
        compression='tar.xz', retention='10 days', rotation='100 MB'
    )
