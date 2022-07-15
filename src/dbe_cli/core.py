import sys
import traceback
from collections import deque
from typing import Optional

from .conf import MODE
from .base_type import Node
from .tfs_cache import TFSCache
from .exceptions import ActionInvalid, ObjectNotExists


class TreeFS:
    """
    Tree structure File System
    """

    def __init__(self) -> None:
        self.root: Node = Node('/')
        self.curr: Node = self.root

        self._build_default_nodes()

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

    def _get_node_by_path(self, path: str, target: Node) -> Node:
        """
        Return node which matches the specific path.

        If path is absolute path, target should be root node,
        else target should be currently working path
        """
        curr = target

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
                    raise ActionInvalid('cursor overflow')
                # Move current cursor to parent
                curr = curr.p_node
            else:
                # Move current cursor to specific
                if _dir not in curr.children:
                    raise ObjectNotExists(f'Object: {_dir} not exists')
                curr = self._get_node_by_name(curr, _dir)

        return curr

    def _mount(self, db_file: str) -> dict[str, Node]:
        self.root.add_child(db_file)
        return self.root.children

    def _unmount(self, db_file: str) -> dict[str, Node]:
        self.root.remove_child(db_file)
        return self.root.children

    def _touch(self, path: str):
        """
        Create file under current dir or specific path
        """
        if '/' not in path:
            name = path
            target = self.curr
        else:
            source = self.root if path.startswith('/') else self.curr

            # Split file name and directory
            path_lst = path.split('/')
            name = path_lst[-1]
            dir_path = '/'.join(path_lst[:-1])
            target = self._get_node_by_path(dir_path, source)
        target.add_attr(name, '')
        return self._ls(target)

    def _mkdir(self, path: str):
        """
        Create directory under current dir or specific path
        """
        if '/' not in path:
            name = path
            target = self.curr
        else:
            source = self.root if path.startswith('/') else self.curr

            # Split file name and directory
            path_lst = path.split('/')
            name = path_lst[-1]
            dir_path = '/'.join(path_lst[:-1])
            target = self._get_node_by_path(dir_path, source)
        target.add_child(name)
        return self._ls(target)

    def _rm(self):
        # Only file and empty directory can be deleted
        # You can use -r to recursive delete dir node
        # if
        pass

    def _find(self):
        pass

    def _ls(self, target: Optional[Node] = None, n_f: str = ''):
        """
        List all filtered nodes or attributes or both of target node.

        n_f: name filter, logic: nf in iter
        """
        # Use current node as default action object if target is None
        target = target or self.curr

        # Check if target is invalid
        if target is None:
            raise ActionInvalid()

        # Compute child nodes
        node_lst = (
            target.children[node_name]
            for node_name in target.children
            if n_f in node_name)

        # Return needed data(node/attr)
        return node_lst

    def _stat(self, target: Optional[Node] = None, n_f: str = ''):
        """
        List all filtered nodes or attributes or both of target node.

        n_f: name filter, logic: nf in iter
        """
        # Use current node as default action object if target is None
        target = target or self.curr

        # Check if target is invalid
        if target is None:
            raise ActionInvalid()

        # Compute attributes
        attr_lst = filter(lambda attr_name: n_f in attr_name, target.attr)
        return attr_lst

    def _tab(self, t_f='*', n_f: str = ''):
        # Return brother nodes' names
        if self.curr.p_node is None:
            raise ActionInvalid('cursor overflow')
        return self._ls(self.curr.p_node, t_f, n_f)

    def _pwd(self):
        """
        Return work directory
        """
        cursor = self.curr
        node_path_lst = []
        while cursor.p_node is not None:
            node_path_lst.append(cursor.name)
            cursor = cursor.p_node

        abs_path = '/'.join(reversed(node_path_lst))
        return abs_path

    def _get_node_by_name(self, target: Node, name: str):
        """
        Search node with specific name in target node's children
        """
        for node_name in target.children:
            if node_name == name:
                return target.children[node_name]
        raise ObjectNotExists(f'Object: {name} not exists')

    def _cd(self, path: str = None):
        # Move current cursor to root if no path below cd command
        if path is None:
            self.curr = self.root
            return

        # Absolute path based on root, while relative path based on current node
        source = self.root if path.startswith('/') else self.curr
        self.curr = self._get_node_by_path(path, source)

    def _tree(self, target: Optional[Node] = None):
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

    def _flush(self):
        pass


if __name__ == "__main__":
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    blue = "\x1b[1;34m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    # print("\x1b[33;20m 23333333 ", "\x1b[0m")
    tfs = TreeFS()

    path = '/'
    mode = 'lazy'
    while True:
        try:
            val = input(f'tfs@{mode}:{path}$ ')
            if val.startswith('ls'):
                print(blue, *[str(x) for x in tfs._ls()[0]], reset,
                      *list(tfs._ls()[1]))
            elif val.startswith('cd'):
                tfs._cd(val.split(' ')[-1])
                path = '/' + tfs._pwd()
            elif val.startswith('tree'):
                print(list(tfs._tree()))
            elif val.startswith('pwd'):
                print('/' + tfs._pwd())
            elif val.startswith('mount'):
                print(*map(lambda x: str(x), tfs._mount(val.split(' ')[-1])))
            elif val.startswith('unmount'):
                print(*map(lambda x: str(x), tfs._unmount(val.split(' ')[-1])))
            elif val.startswith('mkdir'):
                res = tfs._mkdir(val.split(' ')[-1])
                print(blue, *[str(x) for x in res[0]], reset, *list(res[1]))
            elif val.startswith('touch'):
                res = tfs._touch(val.split(' ')[-1])
                print(blue, *[str(x) for x in res[0]], reset, *list(res[1]))
            else:
                print(f'Command {val.split(" ")[0]} not found')
        except KeyboardInterrupt:
            print('bye')
            sys.exit()
        except Exception as e:
            traceback.print_exc()
