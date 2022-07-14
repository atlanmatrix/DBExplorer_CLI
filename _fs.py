from _node import Node
from _tree import Tree


class FS:
    def __init__(self) -> None:
        pass

    def _is_abs_path(self, path: str):
        if path.startswith('/'):
            return True

        return False

    def _to_abs_path(self, curr: Node, path: str):
        if self._is_abs_path(path):
            return path

        
