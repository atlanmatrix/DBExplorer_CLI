"""
Definition of data structure such as Node, Tree, etc.
"""
from typing import Optional, Union, Any

from exceptions import DuplicateNameError, ObjectNotExists, \
    DuplicateAttrNameError, AttrNotExistsError, TFSAttributeError


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
        self.children: dict[str, Node] = {}

    def __str__(self) -> str:
        return self.name

    def add_attr(self, key: str, val: Any):
        """
        Add new attribute to current node

        Raise DuplicateAttrNameError if attribute exists
        """
        if key not in self.attr:
            self.attr[key] = val
        else:
            raise TFSAttributeError(
                f'{self.name} already exists attribute name {key}')

    def del_attr(self, key: str):
        """
        Remove specific key of current node

        Raise AttrNotExistsError if attribute not found
        """
        if key not in self.attr:
            self.attr.pop(key)
        else:
            raise TFSAttributeError(
                f'{self.name} does not exists attribute name {key}')

    def add_child(self, child: Union['Node', str]) -> 'Node':
        """
        Add a child node for current node
        """
        if isinstance(child, Node):
            # If child is Node object, get its name
            child_name = child.name
            child_node = child
        else:
            # If child is string, build new node from the string
            child_name = child
            child_node = Node(child, self)

        # Check if node has the same name as other children
        if child_name in self.children:
            raise TFSAttributeError(
                f'{self.name} already exists attribute name {child_name}')

        # Add node to children dict
        self.children[child_name] = child_node

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
