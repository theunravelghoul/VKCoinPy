import logging
import logging.config

import js2py


def get_pass(e, t):
    return e - 1 + t


def calculate_pow(p: str) -> int:
    context = js2py.EvalJs({
        'window': '{WebSocket: true, Math: Math, parseInt: parseInt}',
    })
    result = context.eval(p)
    return result


def setup_logging(bot_config: dict) -> None:
    log_level = bot_config.get('log_level', 'INFO')
    logging.basicConfig(level=log_level, format='%(threadName)s | %(message)s')
