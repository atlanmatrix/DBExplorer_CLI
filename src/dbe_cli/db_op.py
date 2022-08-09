import requests
import logging

from conf import DBE_SERVER
from utils import parse_req_data

logging.basicConfig(
    filename=r'C:\Users\claude\Documents\dbe_cli\trace.log',
    level=0)
logger = logging.getLogger('main')


__all__ = ['fs_open', 'fs_add', 'fs_ls', 'fs_cd', 'fs_rm']


def fs_open(host, real_path) -> dict[str, dict]:
    """
    Get all nodes' data in real_path
    """
    filename, *path = list(filter(lambda x: x, real_path.split('/')))
    res = requests.post(DBE_SERVER, params={
        'host': host,
        'filename': filename,
        'path': '\\'.join(path)
    })

    if res.status_code == 200:
        req_data = res.json()['data']
        data = parse_req_data(req_data)
        return True, data
    else:
        print('error')
        return False, None


def fs_add(real_path) -> dict[str, dict]:
    pass


def fs_ls():
    # Behavior while open a directory in TFS
    pass


def fs_cd():
    # Behavior while open a directory in TFS
    pass


def fs_rm():
    # Behavior while open a directory in TFS
    pass
