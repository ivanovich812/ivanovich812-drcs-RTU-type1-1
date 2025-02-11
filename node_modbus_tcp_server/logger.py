import os

from loguru import logger


class Logger:
    def __init__(self):
        self.event_types = {'debug': logger.debug,
                            'info': logger.info,
                            'error': logger.error}

        log_file_path = os.path.join('../EVENT_LOG', 'log.log')
        logger.add(log_file_path,
                   level='DEBUG',
                   rotation='500 MB',
                   format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

    def event(self, level, msg):
        action = self.event_types.get(level, None)
        if action is not None:
            action(msg)
