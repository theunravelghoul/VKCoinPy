import logging
import logging.config
import os
import js2py

def setup_logging():
    pass


def get_pass(e, t):
    return e + t - 15 if e % 2 == 0 else e + t - 109


def calculate_pow(p: str) -> int:
    result = js2py.eval_js(p)
    return result


def prepare_logs_dir() -> str:
    logs_dir_name = 'logs'
    logs_dir_path = os.path.abspath(os.path.join(__file__, '..', 'logs'))
    if not os.path.exists(logs_dir_path):
        os.mkdir(logs_dir_path)
    return logs_dir_path


def get_log_file_name(logs_dir_path: str) -> str:
    return os.path.join(logs_dir_path, f'{len(os.listdir(logs_dir_path))}.txt')


def setup_logging(bot_config: dict) -> None:
    log_level = bot_config.get('LOG_LEVEL', 'INFO')

    logs_dir_path = prepare_logs_dir()

    logs_file_name = get_log_file_name(logs_dir_path)
    config = {
        'version': 1,
        'formatters': {
            'detailed': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
            },
            'default': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': get_log_file_name(prepare_logs_dir()),
                'mode': 'w',
                'formatter': 'detailed',
            },
        },
        'root': {
            'level': log_level,
            'handlers': ['console', 'file']
        }
    }
    logging.config.dictConfig(config)
