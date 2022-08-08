from collections import deque
from typing import Optional, Union, Any
from abc import ABC, abstractmethod

from conf import MODE
from base_type import Node
from tfs_cache import TFSCache
from exceptions import NoSuchCommandError, CursorOverflow, \
    ObjectNotExists, InvalidOperationError


class PathDescriptor:
    def __get__(self, instance, owner):
        # Get path of current node
        path = instance.get_abs_path_by_node(instance.curr)
        return path

    def __set__(self, instance, value):
        # Move current node to specific path
        instance.curr = instance.get_node_by_path(value)


class BaseTreeFS(ABC):
    """
    Tree structure File System
    """
    path = PathDescriptor()
    cmd_prefix = '_cmd_'

    def __init__(self, host: str = 'localhost', path: str = '/') -> None:
        self.host = host
        self._cmd = [cmd[len(self.cmd_prefix):] for cmd in dir(self) if
                     cmd.startswith('_cmd')]
        self._history = deque()
        self.root: Node = Node('/')
        self.curr: Node = self.root
        self.prev: Optional[Node] = None

        self._build_default_nodes()

        self.path = path

    def __str__(self):
        return f'cli@{self.host}:/{self.path}$ '

    def cmd_completer(self, text, state):
        """
        Auto-complete supported commands
        """
        options = [cmd for cmd in self._cmd if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

    def parser(self, cmd):
        """
        Split command line string into cmd_name and args,
        and call the corresponding method if it is valid.
        """
        cmd_name, *args = cmd.strip().split()
        cmd_op = getattr(self, f'{self.cmd_prefix}{cmd_name}', None)

        if not cmd_op:
            raise NoSuchCommandError(cmd_name)

        output = cmd_op(*args)
        return output

    def _format_res(self):
        pass

    def _build_default_nodes(self):
        if MODE == 'lazy':
            tfs_cache = TFSCache()
            self.meta = tfs_cache.meta
            self.cache = tfs_cache.cache
        else:
            # Top level node
            db_file_lst = ['master', 'base', 'ccubase', 'Co_1']
            for db_file in db_file_lst:
                self.root.add_child(db_file)

    @staticmethod
    def get_abs_path_by_node(node: Node):
        cursor = node
        node_path_lst = []
        while cursor.p_node is not None:
            node_path_lst.append(cursor.name)
            cursor = cursor.p_node

        abs_path = '/'.join(reversed(node_path_lst))
        return abs_path

    def get_node_by_path(self, path: str, *, insert: bool = False) -> Node:
        """
        Return node which matches the specific path.
        """
        # Handle with absolute path and relative path
        if path.startswith('/'):
            curr = self.root
        else:
            curr = self.curr

        # Deal with symbol
        path_lst = path.split('/')
        for _dir in path_lst:
            _dir = _dir.strip()
            # Support <.|..|str>
            if _dir in ['.', '']:
                continue

            if _dir == '..':
                # Node itself and its parent should exist
                if curr is None or curr.p_node is None:
                    raise CursorOverflow()
                # Move current cursor to parent
                curr = curr.p_node
            else:
                # Move current cursor to specific
                if _dir not in curr.children:
                    if not insert:
                        raise ObjectNotExists(_dir)

                    curr.add_child(_dir)
                curr = self._get_node_by_name(curr, _dir)

        return curr

    @abstractmethod
    def _cmd_ls(self, target: Union[str, Node, None] = None):
        """
        Return node names under given path
        """

    @abstractmethod
    def _cmd_tree(self, target: Optional[Node] = None):
        if target is None:
            target = self.root

        result_lst = []
        node_stack = deque([(0, target)])
        while node_stack:
            level, curr = node_stack.popleft()
            result_lst.append((level, curr.name))
            node_stack.extend(
                [(level + 1, curr.children[node_name]) for node_name in
                 curr.children])

        return result_lst

    @abstractmethod
    def _cmd_cd(self, path: str = None):
        """
        Move current cursor to root if no path below cd command
        """

    @abstractmethod
    def _cmd_mount(self, db_file: str) -> dict[str, Node]:
        """
        Mount behaviors like mkdir,
        but only search append node to root
        """

    @abstractmethod
    def _cmd_unmount(self, db_file: str) -> dict[str, Node]:
        """
        Unmount behaviors like rm(remove),
        but only search node under root
        """

    @abstractmethod
    def _cmd_mkdir(self, path: str, recursive: bool = False):
        """
        Create directory under current dir or specific path
        """

    @abstractmethod
    def _cmd_pwd(self):
        """
        Return work directory
        """

    @abstractmethod
    def _cmd_rm(self, path, recursive: bool = False):
        """
        Only file and empty directory can be deleted if recursive is False
        otherwise, all child node will be removed silently
        """

    @abstractmethod
    def _cmd_find(self, name: str, path: str):
        pass

    @abstractmethod
    def _cmd_stat(self, target, name: str, value: Optional[str] = None):
        """
        List all attributes of target node.
        """

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

    def _cmd_ls(self, path: Optional[str] = None):
        """
        Return node names under given path
        """
        # Use current node as default action object if path is None
        if path is not None:
            target = self.get_node_by_path(path)
        else:
            target = self.curr

        # Compute child nodes
        node_lst = [str(target.children[node_name])
                    for node_name in target.children]

        return ' '.join(node_lst) if node_lst else '<Empty>'

    def _cmd_tree(self, path: Optional[str] = None):
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
                [(level + 1, curr.children[node_name]) for node_name in
                 curr.children])

        for level, node_name in result_lst:
            print('  ' * level + '├──' + node_name)

    def _cmd_cd(self, path: Optional[str] = None):
        # Move current cursor to root if no path below cd command
        if path is None:
            self.curr = self.root
        elif path == '-':
            self.curr, self.prev = self.prev, self.curr
        else:
            # Record current node for later use `cd -` to return
            self.prev = self.curr
            # Absolute path based on root, while relative path based on current node
            self.curr = self.get_node_by_path(path)

    def _cmd_mount(self, db_file: str) -> str:
        """
        Mount behaviors like mkdir,
        but only search append node to root
        """
        self.root.add_child(db_file)
        return f'Mounted "{db_file}" success'

    def _cmd_unmount(self, db_file: str) -> str:
        """
        Unmount behaviors like rm(remove),
        but only search node under root
        """
        self.root.remove_child(db_file)
        return f'Unmounted "{db_file}" success'

    def _cmd_mkdir(self, path: str, recursive: Any = False):
        """
        Create directory under current dir or specific path
        """
        if path == '/':
            raise InvalidOperationError('mkdir under root')

        *dir_path_lst, name = path.split('/')
        dir_path = '/'.join(dir_path_lst)
        target = self.get_node_by_path(dir_path, insert=recursive)
        target.add_child(name)

    def _cmd_pwd(self):
        """
        Return work directory
        """
        return self.get_abs_path_by_node(self.curr)

    def _cmd_rm(self, path: str, recursive: bool = False) -> None:
        """
        Only file and empty directory can be deleted if recursive is False
        otherwise, all child node will be removed silently
        """
        node = self.get_node_by_path(path)
        abs_path = self.get_abs_path_by_node(node)
        path_lst = abs_path.split('/')

        # Root node and db file level node should not be deleted
        if len(path_lst) < 2:
            raise InvalidOperationError('remove root/db file')

        if node.is_leaf():
            node.p_node.children.pop(node.name)
        else:
            # If node contains child nodes, recursive is required to operate removing
            if recursive:
                node.p_node.children.pop(node.name)
            else:
                raise InvalidOperationError('remove node with children')

    def _cmd_find(self, name: str, path: str = None):
        node = self.get_node_by_path(path)

        stack = deque([node])
        path_lst = deque()
        while stack:
            curr = stack.popleft()
            path_lst.append(curr.name)
            if name in curr.name:
                print('/'.join(path_lst))

    def _cmd_stat(self, path: str, name: str, value: Optional[str] = None):
        """
        Get attributes or set one attribute with value
        :param path: path of search root
        :param name: attribute name for get/set
        :param value: if value is not None, do set, else do get
        :return:
        """
        node = self.get_node_by_path(path)

        if name == '*':
            return node.attr

        if value is not None:
            if name in node.attr:
                ret_str = f'Update attribute "{name}" to value "{value}"'
            else:
                ret_str = f'Set value "{value}" a new attribute "{name}"'
            node.attr[name] = value
            return ret_str

        ret_dict = {}
        for attr_name in node.attr:
            if name in attr_name:
                ret_dict[attr_name] = node.attr[attr_name]
        return ret_dict
