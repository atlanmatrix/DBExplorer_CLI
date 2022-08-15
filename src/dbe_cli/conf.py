"""
Configure of DBE-cli
"""
import os


# """
# System mode can be lazy 'mode' or 'rt' mode.
# Lazy mode:
#     Lazy mode can provide high performance if you read more and write less.
#     System will read data from cache(if exists). You can partial flush cache
#     by execute `flush` command.
#     If target not found in cache, it will work like in realtime mode but cache
#     returned data for next use.
# Realtime mode:
#     System will always read data from target third-part system(by hook) and
#     will never use cache.
# """
MODE = 'rt'

# """
# Path of cache file.
# It will be automatically loaded while a new client created, and be updated
# while client exit.
# """

DATA_DIR = '/tmp'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CACHE_FILE = os.path.join(DATA_DIR, 'tfs.cache')
LOG_FILE = os.path.join(DATA_DIR, 'dbe-cli.log')

DBE_SERVER = 'http://192.168.4.24:8888'
REQUIRED_VER = '0.4.1'

LOG_COLOR = {
    'normal': '',
    'success': '',
    'warn': '',
    'reset': ''
}
