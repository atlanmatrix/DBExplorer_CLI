import requests
import logging
from typing import Dict

from .conf import DBE_SERVER
from .utils import parse_req_data

logger = logging.getLogger('main')


__all__ = ['fs_open', 'fs_add', 'fs_rm', 'fs_update',
           'stat_add', 'stat_rm', 'stat_update']


def fs_open(host, real_path) -> Dict[str, dict]:
    """
    Get all nodes' data in real_path
    """
    filename, *path = list(filter(lambda x: x, real_path.split('/')))
    path = '\\'.join(path)
    res = requests.post(f'{DBE_SERVER}/api/db/tree', params={
        'host': host,
        'filename': filename,
        'path': path
    })

    logger.info(f'Get TreeDB data start:')
    logger.info(f'host: "{host}" filename: "{filename}" path: "{path}"')

    if res.status_code == 200:
        if res.json()['code'] == 0:
            data = parse_req_data(res.json()['data'])
            logger.info(f'Get TreeDB data success:')
            logger.debug(data)
            return True, data
        else:
            logger.error(f'Get TreeDB data failed:')
            logger.debug(res.json()['msg'])
            return False, res.json()['msg']
    else:
        logger.error(f'Get TreeDB data failed, response text is:')
        logger.debug(res.text)
        return False, res.text


def fs_add(host, real_path) -> Dict[str, dict]:
    """
    Try to create new node
    """
    *path, sub_key = list(filter(lambda x: x, real_path.split('/')))
    path = '\\'.join(path)

    res = requests.post(f'{DBE_SERVER}/api/db/tree/add', params={
        'host': host,
        'path': path,
        'sub_key': sub_key
    })

    logger.info(f'Insert node:')
    logger.info(f'host: "{host}" sub_key: "{sub_key}" path: "{path}"')

    if res.status_code == 200:
        if res.json()['code'] == 0:
            logger.info(f'Insert node success')
            return True, None
        else:
            logger.error(f'Insert node failed')
            logger.debug(res.json()['msg'])
            return False, res.json()['msg']
    else:
        logger.error(f'Insert node {real_path} failed, response text is:')
        logger.debug(res.text)
        return False, res.text


def fs_rm(host, real_path):
    """
    Behavior while delete a directory in TFS
    """
    path = '\\'.join(real_path.split('/')[1:])
    res = requests.post(f'{DBE_SERVER}/api/db/tree/delete', params={
        'host': host,
        'path': path,
    })

    logger.info(f'Delete node:')
    logger.info(f'host: "{host}" path: "{real_path}"')

    if res.status_code == 200:
        if res.json()['code'] == 0:
            logger.info(f'Delete node success')
            logger.debug(res.json()['data'])
            return True, None
        else:
            logger.error(f'Delete node failed')
            logger.debug(res.json()['msg'])
            return False, res.json()['msg']
    else:
        logger.error(f'Delete node {real_path} failed, response text is:')
        logger.debug(res.text)
        return False, res.text


def fs_update(host, real_path, sub_key):
    # *path, sub_key = list(filter(lambda x: x, real_path.split('/')))
    path = '\\'.join(real_path.split('/')[1:])

    res = requests.post(f'{DBE_SERVER}/api/db/tree/update', params={
        'host': host,
        'path': path,
        'sub_key': sub_key
    })

    logger.info(f'Rename node:')
    logger.info(f'host: "{host}" sub_key: "{sub_key}" path: "{path}"')

    if res.status_code == 200:
        if res.json()['code'] == 0:
            logger.info(f'Rename node success')
            return True, None
        else:
            logger.error(f'Rename node failed')
            logger.debug(res.json()['msg'])
            return False, res.json()['msg']
    else:
        logger.error(f'Rename node failed, response text is:')
        logger.debug(res.text)
        return False, res.text


def stat_add(host, real_path, prop_name, prop_val):
    path = '\\'.join(real_path.split('/')[1:])

    res = requests.post(f'{DBE_SERVER}/api/db/tree/props/update', params={
        'host': host,
        'path': path,
        'prop_name': prop_name,
        'prop_val': prop_val,
    })

    logger.info(f'Update node:')
    logger.info(f'host: "{host}" path: "{path}"'
                f'prop_name: "{prop_name}"  prop_val: "{prop_val}"')

    if res.status_code == 200:
        if res.json()['code'] == 0:
            logger.info(f'Update node attribute success')
            return True, None
        else:
            logger.error(f'Update node attribute failed')
            logger.debug(res.json()['msg'])
            return False, res.json()['msg']
    else:
        logger.error(f'Update node attribute failed, response text is:')
        logger.debug(res.text)
        return False, res.text


def stat_update(*args):
    return stat_add(*args)


def stat_rm(host, real_path, prop_name):
    path = '\\'.join(real_path.split('/')[1:])

    res = requests.post(f'{DBE_SERVER}/api/db/tree/props/delete', params={
        'host': host,
        'path': path,
        'prop_name': prop_name,
    })

    logger.info(f'Delete node attribute:')
    logger.info(f'host: "{host}" path: "{path}" prop_name: "{prop_name}"')

    if res.status_code == 200:
        if res.json()['code'] == 0:
            logger.info(f'Delete node attribute success')
            return True, None
        else:
            logger.error(f'Delete node attribute failed')
            logger.debug(res.json()['msg'])
            return False, res.json()['msg']
    else:
        logger.error(f'Delete node attribute failed, response text is:')
        logger.debug(res.text)
        return False, res.text
