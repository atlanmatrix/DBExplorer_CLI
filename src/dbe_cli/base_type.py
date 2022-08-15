"""
Definition of data structure such as Node, Tree, etc.
"""
from typing import Optional, Any, Dict

from .exceptions import ObjectNotExists, TFSAttributeError


class Node:
    """
    Node definition of TreeFS
    """

    def __init__(self, name: str, p_node: Optional['Node'] = None,
                 attr: Optional[dict] = None) -> None:
        """
        name: node name
        p_node: parent node
        attr: node key-val attr
        """
        self.p_node = p_node
        self.name = name
        self.attr: Optional[dict] = attr or {}
        self.children: Dict[str, Node] = {}
        self.init: bool = False

    def __str__(self) -> str:
        return self.name

    def add_attr(self, key: str, val: Any, overwrite: bool = False):
        """
        Add new attribute to current node

        Raise DuplicateAttrNameError if attribute exists
        """
        if key not in self.attr or overwrite:
            self.attr[key] = val
        else:
            raise TFSAttributeError(
                f'{self.name} already exists attribute name {key}')

    def del_attr(self, key: str):
        """
        Remove specific key of current node

        Raise TFSAttributeError if attribute not found
        """
        if key not in self.attr:
            self.attr.pop(key)
        else:
            raise TFSAttributeError(
                f'{self.name} does not exists attribute name {key}')

    def add_child(self, node_name: str) -> 'Node':
        """
        Add a child node for current node
        """
        child_node = Node(node_name, self)

        # Check if node has the same name as other children
        if node_name in self.children:
            raise TFSAttributeError(
                f'{self.name} already exists node name {node_name}')

        # Add node to children dict
        self.children[node_name] = child_node

        return child_node

    def remove_child(self, child_name: str):
        """
        Remove child node by name
        """
        try:
            return self.children.pop(child_name)
        except KeyError:
            raise ObjectNotExists(child_name)

    def is_leaf(self):
        return len(self.children) == 0

    def to_json(self):
        return self.__dict__


class TFSTree:
    """
    TreeDB File System Tree
    """

    def __init__(self) -> None:
        pass

    def cache_to_tree(self):
        pass

    def tree_to_cache(self):
        pass


class SearchTree:
    """
    Search Tree
    """
    pass


class TrieTree:
    """
    Trie Tree
    """
    pass
