import json
import readline
import logging
from time import time
from collections import deque
from typing import Optional, Any
from functools import wraps

import requests

from .conf import MODE, DBE_SERVER
from .base_type import Node
from .tfs_cache import TFSCache
from .exceptions import NoSuchCommandError, CursorOverflow, \
    ObjectNotExists, InvalidOperationError, HookMethodNotExists, \
    HookMethodExecError, ObjectExists

try:
    from . import db_op
except ImportError:
    db_op = None

logger = logging.getLogger('main')


class PathDescriptor:
    def __get__(self, instance, owner):
        # Get path of current node
        path = instance.full_path(instance.curr)
        return path

    def __set__(self, instance, value):
        # Move current node to specific path
        instance.curr = instance.get_node_by_path(value)


def time_cost(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        st_time = time()
        res = func(self, *args, **kwargs)
        ed_time = time()
        cost = ed_time - st_time
        self.prev_cmd_cost = int(cost * 1000)
        return res
    return wrapper


class LogColor:
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"


class BaseTreeFS:
    """
    Tree structure File System
    """
    path = PathDescriptor()
    cmd_prefix = '_cmd_'

    def __init__(self, host: str = 'localhost', path: str = '/') -> \
            None:
        self.prev_cmd_cost = 0
        self.host = host
        self._cmd = [cmd[len(self.cmd_prefix):] for cmd in dir(self) if
                     cmd.startswith(self.cmd_prefix) and cmd not in [
                         self.cmd_prefix + p_cmd for p_cmd in ['debug']
                     ]]
        self.root: Node = Node('/')
        self.curr: Node = self.root
        self.prev: Optional[Node] = None

        self._get_db_info()

        self._build_default_nodes()

        self.path = path
        self._hooks = self._register_hook(db_op)

    @staticmethod
    def _register_hook(mod):
        if mod is None:
            raise ModuleNotFoundError('db_op')

        hook_lst = ['fs_open', 'fs_add', 'fs_rm', 'fs_update',
                    'stat_get', 'stat_add', 'stat_rm', 'stat_update']
        hooks = {}

        for hook in hook_lst:
            hooks[hook] = getattr(mod, hook, None)

        return hooks

    def _get_db_info(self):
        print('Loading data from DBE Server...')
        db_info_url = f'{DBE_SERVER}/api/cfg/host'
        res = requests.get(db_info_url)

        if res.status_code == 200:
            res_data = res.json()['data']
            logger.info(res_data)
            self.db_info = {
                db['host']: {
                    'files': [file['name'] for file in db['dbFiles']],
                    'name': db['name']
                }
                for db in res_data
            }
            logging.info(self.db_info)
            print('Loading data success！')
        else:
            logger.error(res.text)
            self.db_info = None
            print('Loading data failed, please check if your DBE server '
                  'accessible')

    def __str__(self):
        cost_s = str(self.prev_cmd_cost)
        if self.prev_cmd_cost < 100:
            legacy_color = LogColor.green
        elif self.prev_cmd_cost < 800:
            legacy_color = LogColor.yellow
        else:
            legacy_color = LogColor.red

        if cost_s == '0':
            cost_s = '<1'

        return f'{legacy_color}[{cost_s}ms]{LogColor.reset}' \
               f'cli' \
               f'@' \
               f'{self.host}' \
               f':' \
               f'{LogColor.blue}{self.path}{LogColor.reset}' \
               f'$ '

    def cmd_completer(self, text, state):
        """
        Auto-complete supported commands
        """
        full_cmd = readline.get_line_buffer()
        cmd_lst = full_cmd.split()
        if len(cmd_lst) == 0:
            return self._cmd[state]

        m_cmd, *args = cmd_lst
        if len(cmd_lst) == 1:
            if not full_cmd[-1] == ' ':
                options = [cmd for cmd in self._cmd if cmd.startswith(m_cmd)]
            else:
                if m_cmd == 'connect':
                    options = list(self.db_info)
                elif m_cmd in ['?', 'h', 'help']:
                    options = self._cmd
                else:
                    options = [cmd for cmd in self.curr.children if cmd.startswith('')]
        elif len(cmd_lst) == 2:
            op_node = self.curr
            sub_cmd = args[0]

            if m_cmd == 'connect':
                options = [host
                           for host in self.db_info
                           if host.startswith(sub_cmd)
                           ]
            elif m_cmd in ['?', 'h', 'help']:
                options = [cmd for cmd in self._cmd if cmd.startswith(sub_cmd)]
            else:
                options = [cmd for cmd in op_node.children if cmd.startswith(
                    sub_cmd)]

        if state < len(options):
            return options[state]
        else:
            return None

    def parser(self, cmd):
        """
        Split command line string into cmd_name and args,
        and call the corresponding method if it is valid.
        """
        try:
            cmd_name, *args = cmd.strip().split()
        except ValueError:
            # Ignore empty input
            return

        if cmd_name in ['?', 'h', 'help']:
            # Shortcut for help
            cmd_name = 'help'
            args = args or ['help']

        cmd_op = getattr(self, f'{self.cmd_prefix}{cmd_name}', None)

        if not cmd_op:
            raise NoSuchCommandError(cmd_name)

        output = cmd_op(*args)
        return output

    def _build_default_nodes(self):
        if MODE == 'lazy':
            tfs_cache = TFSCache()
            self.meta = tfs_cache.meta
            self.cache = tfs_cache.cache
        else:
            # Top level node
            if self.db_info is not None and self.host in self.db_info:
                db_file_lst = self.db_info[self.host]['files']
            else:
                db_file_lst = ['master', 'base', 'ccubase', 'Co_1']
            for db_file in db_file_lst:
                self.root.add_child(db_file)

    @staticmethod
    def full_path(node: Node):
        cursor = node
        node_path_lst = []
        while cursor.p_node is not None:
            node_path_lst.append(cursor.name)
            cursor = cursor.p_node

        abs_path = '/' + '/'.join(reversed(node_path_lst))
        return abs_path

    @staticmethod
    def _real_path_to_lst(real_path):
        return list(filter(lambda x: x, real_path.split('/')))

    def _get_dirname(self, real_path):
        dir_name, _ = self._path_split(real_path)
        return dir_name

    def _get_basename(self, real_path):
        _, base_name = self._path_split(real_path)
        return base_name

    def _path_split(self, path):
        real_path = self._real_path(path)
        *dir_path_lst, base_name = self._real_path_to_lst(real_path)
        dir_name = '/' + '/'.join(dir_path_lst)

        return dir_name, base_name

    def _real_path(self, path):
        """
        Convert path with '.' and '..' to real path
        """
        abs_path = path
        if not path.startswith('/'):
            abs_path = self.abs_path(path)

        real_path_lst = []
        abs_path_lst = abs_path.split('/')

        for _dir in abs_path_lst:
            if _dir in ['.', '']:
                continue

            if _dir == '..':
                if len(real_path_lst) == 0:
                    raise CursorOverflow()
                real_path_lst.pop()
            else:
                real_path_lst.append(_dir)
        real_path = '/' + '/'.join(real_path_lst)
        return real_path

    @staticmethod
    def _is_inited(target, node_name):
        """

        """
        if node_name not in target.children:
            # Does not exist
            return False

        if not target.children[node_name].init:
            # Exist but not inited
            return False

        return target.children[node_name]

    def abs_path(self, rel_path):
        """
        Convert relative to absolute path
        """
        p_path = self.full_path(self.curr)
        path = f'{p_path}/{rel_path}'
        return path

    def _build_node_from_db(self, real_path_lst, node_data):
        curr = self.root
        logger.info('Build node from DB')
        logger.debug(f'real_path_lst: "{real_path_lst}"')
        logger.debug(node_data)
        for _dir in real_path_lst:
            if _dir not in curr.children:
                curr.add_child(_dir)
                logger.debug(f'Add new node {_dir}')
            logger.debug(curr)
            curr = curr.children[_dir]
            logger.debug(f'Move to {_dir}')

        if node_data is not None and not curr.init:
            for attr_name, attr_val in node_data['attr'].items():
                logger.debug(f'Add new attribute {attr_name}: {attr_val}')
                curr.add_attr(attr_name, attr_val, True)

            for node_name in node_data['children']:
                logger.debug(f'Add new node {_dir}')
                curr.add_child(node_name)
            curr.init = True
        return curr

    def get_node_by_path(self, path: str, *, insert: bool = False) -> \
            Node:
        """
        Return node which matches the specific path.
        """
        logger.info('Invoke get_node_by_path')
        logger.debug(f'path: {path}')
        real_path = self._real_path(path)
        real_path_lst = self._real_path_to_lst(real_path)
        logger.debug(f'real_path: {real_path}')

        # Search TFS tree
        curr = self.root
        for _dir in real_path_lst:
            logger.debug(f'find node: {_dir}')
            if not self._is_inited(curr, dir):
                hook_name = 'fs_open'
                logger.debug(f'is inited: False')
                logger.info(f'invoke hook: {hook_name}')
                # Node not found in TFS Tree, search DB if the hook exists
                hook_open = self._hooks.get(hook_name)
                if not hook_open:
                    logger.debug(f'hook {hook_name} not exists')
                    raise HookMethodNotExists(hook_name)

                res, nodes_data = hook_open(self.host, real_path)
                if not res:
                    logger.debug(f'hook {hook_name} execute error')
                    raise HookMethodExecError(hook_name, nodes_data)

                # Build tree node, this will build full chains,
                # so we should break loop after build
                curr = self._build_node_from_db(real_path_lst, nodes_data)
                break

            logger.debug(f'is inited: True')
            curr = curr.children[_dir]
        return curr

    def _get_node_by_name(self, target: Node, name: str):
        """
        Search node with specific name in target node's children
        """
        for node_name in target.children:
            if node_name == name:
                return target.children[node_name]
        raise ObjectNotExists(f'Object: {name} not exists')


class TreeFS(BaseTreeFS):
    def __init__(self, host: str = 'localhost', path: str = '/'):
        super(TreeFS, self).__init__(host, path)

    @time_cost
    def _cmd_connect(self, host):
        """
        Connect to DB instance, this will reinit cache tree

        Usage:
            connect <domain|ip>
        """
        self.host = host
        self.root: Node = Node('/')
        self.curr: Node = self.root
        self.prev: Optional[Node] = None

        self._build_default_nodes()

        return f'Host has been changed to "{self.host}"'

    @time_cost
    def _cmd_help(self, cmd: str = ''):
        """
        Print helpful information for commands

        *   You can press `TAB` key twice to view all commands
        **  You can also press `TAB` to auto-complete node name

        PAY ATTENTION:
        * This system use **lazy load** mechanism to avoid frequently DB
        operations and speed up your access.
        * Because of this reason, if **others** change DB data, you may not be
        notified until one action be triggered to update **virtual tree**.
        * But if you modify the database yourself, the cache tree will also
        be updated, it is real-time.

        If you have any questions while using this program, create issues here:
        https://github.com/atlanmatrix/DBExplorer_CLI/issues

        Usage:
            ? [cmd]
            h [cmd]
            help [cmd]
        """
        cmd_obj = getattr(self, self.cmd_prefix + cmd, None)
        if cmd_obj is not None:
            return cmd_obj.__doc__

    @time_cost
    def _cmd_debug(self, path=None):
        """
        View the specified node information

        Usage:
            debug [path]
        """
        if path is None:
            node = self.curr
        else:
            node = self.get_node_by_path(path)

        print(node.to_json())

    @time_cost
    def _cmd_ls(self, path: Optional[str] = None, f_str: str = ''):
        """
        List all child nodes of specific node,
        if not specified, it will list child nodes of current node

        Usage:
            ls [node_path] [filter]
        """
        # Use current node as default action object if path is None
        if path is not None:
            target = self.get_node_by_path(path)
        else:
            target = self.curr

        # Compute child nodes
        node_lst = [str(target.children[node_name])
                    for node_name in target.children
                    if f_str in node_name]

        return LogColor.blue \
               + ' '.join(node_lst) if node_lst else '<Empty>' \
               + LogColor.reset

    @time_cost
    def _cmd_tree(self, path: Optional[str] = None, f_str: str = ''):
        """
        Print all nodes in specific node as a tree of **virtual tree**

        PAY ATTENTION:
        * If you try visit some node which has not cached in **virtual
        tree**, it will try fetch data from DB and cached them.

        Usage:
            tree [path] [filter]
        """
        if path is None:
            node = self.curr
        else:
            node = self.get_node_by_path(path)

        result_lst = []
        node_stack = deque([(0, node)])
        while node_stack:
            level, curr = node_stack.pop()
            result_lst.append((level, curr.name))
            node_stack.extend(
                [(level + 1, curr.children[node_name])
                 for node_name in curr.children if f_str in node_name])

        for level, node_name in result_lst:
            print('  ' * level + '├──' + node_name)

    @time_cost
    def _cmd_cd(self, path: Optional[str] = None):
        """
        Move to specific node

        PAY ATTENTION:
        Command `cd` will prefer cache data rather than requests for DB,
        if you want real-time data in DB, you should use `flush`

        Usage:
            cd              Behavior like `cd /`
            cd -            Move to previous node
            cd <path>       Move to specific node
        """
        logger.info('Invoke cd')
        logger.debug(f'path: {path}')

        if path is None:
            self.curr = self.root
        elif path == '-':
            self.curr, self.prev = self.prev, self.curr
        else:
            # Record current node for later use `cd -` to return
            self.prev = self.curr
            # Absolute path based on root,
            # while relative path based on current node
            self.curr = self.get_node_by_path(path)

    @time_cost
    def _cmd_flush(self):
        """
        Get real-time data from DB, this may take more time and reduce your
        experience, if you don't particularly need real-time data,
        you should use `cd` command

        Usage:
            flush
        """
        self.curr.init = False
        self.curr.stat = {}
        self.curr.children = {}
        # Refresh cache
        self._cmd_cd('.')
        self._cmd_ls('.')

    @time_cost
    def _cmd_mount(self, db_file: str) -> str:
        """
        Mount behaviors like mkdir, but only append node to `root`

        Usage:
            mount <dev>
        """
        self.root.add_child(db_file)
        return f'Mounted "{db_file}" success'

    @time_cost
    def _cmd_unmount(self, db_file: str) -> str:
        """
        Unmount behaviors like rm(remove), but only search node in `root`

        Usage:
            unmount <dev>
        """
        self.root.remove_child(db_file)
        return f'Unmounted "{db_file}" success'

    @time_cost
    def _cmd_mkdir(self, path: str, recursive: Any = False):
        """
        Create new node in specific node

        Usage:
            mkdir <path>
        """
        logger.info('Invoke: _cmd_mkdir')
        if path == '/':
            raise InvalidOperationError('mkdir under root')

        dir_name, base_name = self._path_split(path)
        logger.debug(f'dir_name: "{dir_name}" base_name: "{base_name}"')

        try:
            curr = self.get_node_by_path(dir_name)
        except ObjectNotExists as e:
            if not recursive:
                raise ObjectNotExists(e)
            else:
                raise NotImplementedError('Mkdir with recursive param is not '
                                          'supported')

        hook_name = 'fs_add'
        hook_add_node = self._hooks.get(hook_name)
        if not hook_add_node:
            raise HookMethodNotExists(hook_name)

        real_path = self._real_path(path)
        logger.debug(f'real_path: "{real_path}"')
        res, err_msg = hook_add_node(self.host, real_path)

        if not res:
            raise HookMethodExecError(hook_name, err_msg)
        curr.add_child(base_name)

    @time_cost
    def _cmd_mv(self, old_path, new_path):
        """
        Move child in current node

        Usage:
            mv <old_path> <new_path>
        """
        if '/' in old_path or '/' in new_path:
            raise ValueError('ERROR: You can only move nodes under the same '
                             'parent node')

        self._cmd_rename(old_path, new_path)

    @time_cost
    def _cmd_rename(self, old_name, new_name):
        """
        Rename child in current node

        Usage:
            rename <old_name> <new_name>
        """
        p_path = self.full_path(self.curr)

        if old_name not in self.curr.children:
            raise ObjectNotExists(old_name)

        if new_name in self.curr.children:
            raise ObjectExists(new_name)

        hook_name = 'fs_update'
        hook_update_node = self._hooks.get(hook_name)
        if not hook_update_node:
            raise HookMethodNotExists(hook_name)

        real_path = self._real_path(p_path)
        logger.debug(f'real_path: "{real_path}"')
        res, err_msg = hook_update_node(
            self.host, f'{real_path}/{old_name}', new_name)

        if not res:
            raise HookMethodExecError(hook_name, err_msg)

        # Destroy node data
        self.curr.init = False
        self.curr.stat = {}
        self.curr.children = {}
        # Refresh cache
        self._cmd_cd('.')

    @time_cost
    def _cmd_pwd(self):
        """
        Print working directory

        Usage:
            pwd
        """
        return self.full_path(self.curr)

    @time_cost
    def _cmd_rm(self, path: str, recursive: bool = False) -> None:
        """
        Remove a node

        Usage:
            rm <path>
        """
        node = self.get_node_by_path(path)
        abs_path = self.full_path(node)
        path_lst = abs_path.split('/')

        # Root node and db file level node should not be deleted
        if len(path_lst) < 2:
            raise InvalidOperationError('remove root/db file')

        hook_name = 'fs_rm'
        hook_fs_rm = self._hooks.get(hook_name)
        if not hook_fs_rm:
            raise HookMethodNotExists(hook_name)

        real_path = self._real_path(path)
        res, err_msg = hook_fs_rm(self.host, real_path)

        if not res:
            raise HookMethodExecError(hook_name, err_msg)
        # Destroy node data
        p_node = node.p_node
        p_node.init = False
        p_node.stat = {}
        p_node.children = {}
        # Refresh cache
        self._cmd_cd('.')

    @time_cost
    def _cmd_find(self, name: str, path: str = None):
        """
        Search for files in a node

        Usage:
            find name [path]
        """
        raise NotImplementedError('Command `find` has not been implemented')

    @time_cost
    def _cmd_stat(self, path: str = '.', name: str = '*',
                  value: Optional[str] = None):
        """
        Get attribute(s) of a node or set one attribute of a node,
        get or set depends on whether the third parameter is provided

        Usage:
            stat [node_path] [filter] [value]
        """
        node = self.get_node_by_path(path)

        if name == '*':
            return json.dumps(node.attr, indent='  ', ensure_ascii=False)

        if value is not None:
            if name in node.attr:
                hook_name = 'stat_add'
                hook_add_attr = self._hooks.get(hook_name)
                if not hook_add_attr:
                    raise HookMethodNotExists(hook_name)

                real_path = self._real_path(path)
                logger.debug(f'real_path: "{real_path}"')
                res, err_msg = hook_add_attr(self.host, real_path, name, value)

                if not res:
                    raise HookMethodExecError(hook_name, err_msg)
            else:
                hook_name = 'stat_update'
                hook_update_attr = self._hooks.get(hook_name)
                if not hook_update_attr:
                    raise HookMethodNotExists(hook_name)

                real_path = self._real_path(path)
                logger.debug(f'real_path: "{real_path}"')
                res, err_msg = hook_update_attr(self.host, real_path, name, value)

                if not res:
                    raise HookMethodExecError(hook_name, err_msg)
            node.attr[name] = value

        ret_dict = {}
        for attr_name in node.attr:
            if name in attr_name:
                ret_dict[attr_name] = node.attr[attr_name]
        return json.dumps(ret_dict, indent='  ', ensure_ascii=False)

    @time_cost
    def _cmd_rmstat(self, path: str = '.', name: str = None):
        """
        Remove one attribute from specific node, default node is current

        Usage:
            rmstat [node_path] <attribute_name>
        """
        if not name:
            name = path
            path = '.'
        node = self.get_node_by_path(path)

        hook_name = 'stat_rm'
        hook_stat_rm = self._hooks.get(hook_name)
        if not hook_stat_rm:
            raise HookMethodNotExists(hook_name)

        real_path = self._real_path(path)
        res, err_msg = hook_stat_rm(self.host, real_path, name)

        if not res:
            raise HookMethodExecError(hook_name, err_msg)

        node.init = False
        node.attr = {}
