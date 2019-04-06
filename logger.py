import logging

import crayons

logger = logging.getLogger()


class Logger(object):
    @staticmethod
    @boundaries(logger.info)
    def log_success(message: str) -> None:
        logger.info(crayons.green(message))

    @staticmethod
    @boundaries(logger.info)
    def log_warning(message: str) -> None:
        logger.info(crayons.magenta(message))

    @staticmethod
    @boundaries(logger.error)
    def log_error(message: str) -> None:
        logger.error(crayons.red(message))

    @staticmethod
    @boundaries(logger.info)
    def log_system(message: str) -> None:
        logger.info(crayons.yellow(message))
