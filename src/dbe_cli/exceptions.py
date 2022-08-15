import logging


logger = logging.getLogger('main')


class TFSBaseException(Exception):
    def __init__(self, obj, message):
        err_msg = f'{type(obj)}: {message}'
        logger.error(err_msg)
        super().__init__(err_msg)


class NoSuchCommandError(TFSBaseException):
    def __init__(self, message):
        err_msg = f'Command "{message}" not exists'
        logger.error(err_msg)
        super().__init__(self, err_msg)


class CursorOverflow(TFSBaseException):
    def __init__(self):
        err_msg = 'Cursor overflow'
        logger.error(err_msg)
        super().__init__(self, err_msg)


class InvalidOperationError(TFSBaseException):
    def __init__(self, message):
        err_msg = f'Operation "{message}" is invalid'
        logger.error(err_msg)
        super().__init__(self, err_msg)


class TFSAttributeError(TFSBaseException):
    def __init__(self, message):
        err_msg = message
        logger.error(err_msg)
        super().__init__(self, err_msg)


class ObjectNotExists(TFSBaseException):
    def __init__(self, message):
        err_msg = f'Object "{message}" not exists'
        logger.error(err_msg)
        super().__init__(self, err_msg)


class ObjectExists(TFSBaseException):
    def __init__(self, message):
        err_msg = f'Object "{message}" exists'
        logger.error(err_msg)
        super().__init__(self, err_msg)


class HookMethodNotExists(TFSBaseException):
    def __init__(self, message):
        err_msg = f'Hook "{message}" not exists'
        logger.error(err_msg)
        super().__init__(self, err_msg)


class HookMethodExecError(TFSBaseException):
    def __init__(self, name, message):
        err_msg = f'Hook "{name}" executed failed: {message}'
        logger.error(err_msg)
        super().__init__(self, err_msg)


class CacheDataCorrupted(TFSBaseException):
    pass


class CacheUnexpectedError(TFSBaseException):
    pass
