class ActionInvalid(Exception):
    pass


class DuplicateNameError(Exception):
    """
    After create/move/rename operation, if object has the same name of
    brothers, DuplicateNameError will raised
    """
    pass


class DuplicateAttrNameError(Exception):
    """
    """
    pass


class ObjectNotExists(Exception):
    """

    """
    pass


class AttrNotExistsError(Exception):
    """
    """
    pass


class TFSUnexpectedError(Exception):
    pass
