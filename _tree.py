from typing import Optional

from _node import Node


class Tree:
    def __init__(self) -> None:
        pass

    # def _get_node_by_name(self):
    #     pass

    def _get_path_by_name(self, name: str, root: Node):
        pass

    def _get_path_by_node(self, node: Node):
        cusor: Optional[Node] = node

        path_lst: list[str] = []
        while cusor:
            path_lst.append(cusor.name)
            cusor = cusor.p_node

        return reversed(path_lst)

    def _from_lst(self):
        pass

    def _to_lst(self, mode: str, direct: Optional[str]='l2r') -> list:
        """
        Available node value: ['dfs', 'wfs']
        """
        pass
