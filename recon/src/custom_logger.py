import json
import logging
import os


LOGGER = logging.getLogger(__name__)

LOG_DIR = os.environ['LOG_DIR']


def extra(trace_id, **kwargs):
    return {'trace_id': trace_id, 'kwarg': kwargs}


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'trace_id': getattr(record, 'trace_id', None),
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'kwarg': getattr(record, 'kwarg', None),
        })


def configure_log():
    formatter = JsonFormatter()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    os.makedirs(LOG_DIR, exist_ok=True)
    log_file_path = os.path.join(LOG_DIR, 'recon.log')
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(console_handler)
    LOGGER.addHandler(file_handler)