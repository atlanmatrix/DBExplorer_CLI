import requests
import logging

from conf import DBE_SERVER
from utils import parse_req_data

logger = logging.getLogger('main')


__all__ = ['fs_open', 'fs_add', 'fs_ls', 'fs_cd', 'fs_rm']


def fs_open(host, real_path) -> dict[str, dict]:
    """
    Get all nodes' data in real_path
    """
    filename, *path = list(filter(lambda x: x, real_path.split('/')))
    res = requests.post(f'{DBE_SERVER}/api/db/tree', params={
        'host': host,
        'filename': filename,
        'path': '\\'.join(path)
    })

    if res.status_code == 200:
        req_data = res.json()['data']
        data = parse_req_data(req_data)
        logger.info(f'Get TreeDB data success:')
        logger.debug(data)
        return True, data
    else:
        logger.error(f'Get TreeDB data failed, response text is:')
        logger.debug(res.text)
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
