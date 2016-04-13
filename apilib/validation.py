import collections

class Validator(object):
    documentation = ''

    def validate(self, value, error_context, context):
        return value

    def get_documentation(self):
        return self.documentation

class ValidationError(object):
    def __init__(self, path, code, msg):
        self.path = path
        self.code = code
        self.msg = msg

    def __str__(self):
        return '%s: %s at "%s" - %s' % (self.__class__.__name__, self.code, self.path, self.msg)

class ErrorContext(object):
    def __init__(self, path=''):
        self.path = path
        self.errors = []
        self.children = []

    def add_error(self, error_code, error_msg):
        self.errors.append(ValidationError(self.path, error_code, error_msg))
        return self

    # Use exactly on keyword argument
    def extend(self, field=None, index=None, key=None):
        if field:
            if self.path:
                path = '%s.%s' % (self.path, field)
            else:
                path = field
        elif index is not None:
            path = '%s[%d]' % (self.path, index)
        elif key is not None:
            path = '%s["%s"]' % (self.path, key)
        else:
            raise TypeError('Must specify exactly one keyword arg of either field=, index=, or key=')
        ec = ErrorContext(path)
        self.children.append(ec)
        return ec

    def all_errors(self):
        errors = self.errors[:]
        for child in self.children:
            errors.extend(child.all_errors())
        return errors

    def has_errors(self):
        return bool(self.all_errors())

    def __str__(self):
        return '<%s: %s>' % (type(self).__name__, ', '.join(str(e) for e in self.all_errors()))

class CommonErrorCodes(object):
    INVALID_TYPE = 'INVALID_TYPE'
    INVALID_VALUE = 'INVALID_VALUE'
    UNKNOWN_FIELD = 'UNKNOWN_FIELD'
    REQUIRED = 'REQUIRED'
    AMBIGUOUS = 'AMBIGUOUS'
    NONEMPTY_ITEM_REQUIRED = 'NONEMPTY_ITEM_REQUIRED'
    DUPLICATE_VALUE = 'DUPLICATE_VALUE'
    VALUE_NOT_IN_RANGE = 'VALUE_NOT_IN_RANGE'
    REPEATED = 'REPEATED'

class ValidationContext(object):
    def __init__(self, method=None, service=None, parent=None):
        self.method = method
        self.service = service
        self.parent = parent

    def for_parent(self, parent):
        return ValidationContext(self.method, self.service, parent)

class MethodMatcher(object):
    ServiceMethod = collections.namedtuple('ServiceMethod', ['service', 'method'])

    def __init__(self, method_names):
        self.service_methods = []
        for method_name in method_names or []:
            parts = method_name.split('.')
            if len(parts) == 1:
                service_method = self.ServiceMethod(service=None, method=parts[0])
            else:
                service_method = self.ServiceMethod(service=parts[0], method=parts[1])
            self.service_methods.append(service_method)

    def matches(self, method, service=None):
        if not self.service_methods:
            return True
        if not method and not service:
            return False
        for service_method in self.service_methods:
            if (service_method.method == method
                and (service_method.service == service or service_method.service is None)):
                return True
        return False
