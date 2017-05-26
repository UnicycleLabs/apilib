class ApilibException(Exception):
    pass


class UnknownFieldException(ApilibException):
    pass

class ModuleRequired(ApilibException):
    pass

class ConfigurationRequired(ApilibException):
    pass

class NotInitialized(ApilibException):
    pass

class DeserializationError(ApilibException):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return 'DeserializationError:\n  %s' % '\n  '.join(str(e) for e in self.errors)

class MethodNotFoundException(ApilibException):
    pass

class MethodNotImplementedException(ApilibException):
    pass
