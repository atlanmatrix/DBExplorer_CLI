import sys
import logging

import requests
try:
    import readline
except ImportError:
    import pyreadline as readline

from conf import DBE_SERVER, REQUIRED_VER
from exceptions import TFSBaseException
from core import TreeFS


logging.addLevelName(logging.INFO + 5, 'SUCCESS')


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


f_handler = logging.FileHandler('/tmp/dbe-cli.log')
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(CustomFormatter())

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        f_handler,
    ]
)
logger = logging.getLogger('main')


def main():
    # Check version
    res = requests.get(f'{DBE_SERVER}/api/sys/info')
    if res.status_code == 200:
        sys_info = res.json()['data']
        print('Check server version...')
        logger.info('Check server version...')
        if (server_ver := sys_info.get('ver', '')) < REQUIRED_VER:
            logger.error(f'Server version {server_ver} is too low: '
                         f'at least >= {REQUIRED_VER}')
            print(f'Server version {server_ver} is too low: '
                  f'at least >= {REQUIRED_VER}')
            return

        logger.info('Check passed')
        print('Check passed')
    else:
        logger.error('Get server version failed: ')
        logger.debug(res.text)
        return

    tfs = TreeFS()
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tfs.cmd_completer)

    while True:
        try:
            cmd = input(tfs)
            if cmd == 'q':
                break

            res = tfs.parser(cmd)
            res and print(res)
        except TFSBaseException as e:
            print(e)
        except KeyboardInterrupt:
            print('bye')
            sys.exit()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
