"""
Definition of data structure such as Node, Tree, etc.
"""
from typing import Optional, Union, Any

from .exceptions import DuplicateNameError, ObjectNotExists, \
    DuplicateAttrNameError, AttrNotExistsError


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
            raise DuplicateAttrNameError(
                f'Attribute {key} of {self.name} has exist')

    def del_attr(self, key: str):
        """
        Remove specific key of current node

        Raise AttrNotExistsError if attribute not found
        """
        if key not in self.attr:
            self.attr.pop(key)
        else:
            raise AttrNotExistsError(
                f'Attribute {key} of {self.name} not exist')

    def add_child(self, child: Union['Node', str]) -> None:
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
            raise DuplicateNameError(child_name)

        # Add node to children dict
        self.children[child_name] = child_node

    def remove_child(self, child_name: str):
        """
        Remove child node by name
        """
        try:
            self.children.pop(child_name)
        except KeyError:
            raise ObjectNotExists(f'Object: {child_name} not exist')


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
