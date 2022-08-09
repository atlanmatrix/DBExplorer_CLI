class TFSBaseException(Exception):
    def __init__(self, obj, message):
        super().__init__(f'{type(obj)}: {message}')


class NoSuchCommandError(TFSBaseException):
    def __init__(self, message):
        super().__init__(self, f'Command "{message}" not exists')


class CursorOverflow(TFSBaseException):
    def __init__(self):
        super().__init__(self, 'Cursor overflow')


class InvalidOperationError(TFSBaseException):
    def __init__(self, message):
        super().__init__(self, f'Operation "{message}" is invalid')


class TFSAttributeError(TFSBaseException):
    def __init__(self, message):
        super().__init__(self, message)


class ObjectNotExists(TFSBaseException):
    def __init__(self, message):
        super().__init__(self, f'Object "{message}" not exists')


class CacheDataCorrupted(TFSBaseException):
    pass


class CacheUnexpectedError(TFSBaseException):
    pass
