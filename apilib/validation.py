import collections
import re

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
    def __init__(self, service=None, method=None, operator=None, parent=None):
        self.service = service
        self.method = method
        self.operator = operator
        # Note that the parent is a dictionary and not a model object, since
        # the parent cannot be parsed into a model until its field have been validated.
        self.parent = parent

    def for_parent(self, parent):
        return ValidationContext(self.service, self.method, self.operator, parent)

class InvalidMethodSpec(Exception):
    '''Method specs have the form [service].[method]/[operator]. The service and operator are optional'''

    def __init__(self, method_spec):
        super(InvalidMethodSpec, self).__init__(
            'Method spec "%s" is invalid. Method specs have the form [service].[method]/[operator]' % method_spec)

class MethodMatcher(object):
    ServiceMethod = collections.namedtuple('ServiceMethod', ['service', 'method', 'operator'])

    MATCHER_RE = re.compile('((\w+)\.)?(\w+)(/(\w+))?')

    def __init__(self, method_spec):
        if method_spec is True:
            self.all = True
            self.service_methods = None
            self.method_names = None
        else:
            self.all = False
            self.service_methods = []
            self.method_names = [method_spec] if type(method_spec) in (str, unicode) else method_spec
            for method_name in self.method_names:
                match = self.MATCHER_RE.match(method_name)
                if not match:
                    raise InvalidMethodSpec(method_name)
                service_method = self.ServiceMethod(service=match.group(2), method=match.group(3), operator=match.group(5))
                self.service_methods.append(service_method)

    def for_all_methods(self):
        return self.all

    def methods(self):
        return self.method_names

    def matches(self, service, method, operator):
        if self.all:
            return True
        if not (service or method or operator):
            return False
        for service_method in self.service_methods:
            if (service_method.method == method
                and (service_method.service == service or service_method.service is None)
                and (service_method.operator == operator or service_method.operator is None)):
                return True
        return False
