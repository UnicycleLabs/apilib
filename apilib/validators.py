import decimal

from .validation import CommonErrorCodes
from .validation import MethodMatcher
from .validation import Validator

# Not all falsey values should be considered 'empty', i.e. 0, 0.0, and False
EMPTY_VALUES = (None, [], {}, '')

class Required(Validator):
    '''Usage: Required(), Required('mutate'), Required(['mutate/ADD', 'someservice.get'])'''

    def __init__(self, method_spec=True):
        self.method_matcher = MethodMatcher(method_spec)

    def get_documentation(self):
        if self.method_matcher.for_all_methods():
            return 'Value is required'
        return 'Value is required for methods: %s' % ', '.join(self.method_matcher.methods())

    def validate(self, value, error_context, context):
        if value in EMPTY_VALUES:
            if self.method_matcher.matches(context.service, context.method, context.operator):
                if self.method_matcher.for_all_methods():
                    msg = 'Field is required'
                else:
                    msg = 'Field is required on method(s) "%s"' % ', '.join(self.method_matcher.methods())
                error_context.add_error(CommonErrorCodes.REQUIRED, msg)
                return None
        return value

class Readonly(Validator):
    '''Usage: Readonly(), Readonly('mutate'), Readonly(['mutate/ADD', 'someservice.get'])
    Does not return validation errors, but parses any field as None if it matches the method spec.
    '''
    def __init__(self, method_spec=True):
        self.method_matcher = MethodMatcher(method_spec)

    def get_documentation(self):
        if not self.method_matcher.for_all_methods():
            return 'Value is read-only'
        return 'Value is read-only for method(s): %s' % ', '.join(self.method_matcher.methods())

    def validate(self, value, error_context, context):
        if self.method_matcher.matches(context.service, context.method, context.operator):
            return None
        return value

class NonemptyElements(Validator):
    '''Usage: NonemptyElements()
    [0, 1, 2] --> Valid
    [{'id': 1}, {'id': 2}] --> Valid
    [None] --> Invalid
    ['foo', ''] --> Invalid
    [[], ['a', 'b', 'c']] --> Invalid
    [{}] --> Invalid
    Only works for lists, but lists of any type.
    '''
    documentation = 'Nonempty elements are required'

    def validate(self, value, error_context, context):
        for i, item in enumerate(value or []):
            if item in EMPTY_VALUES:
                error_context.extend(index=i).add_error(
                    CommonErrorCodes.NONEMPTY_ITEM_REQUIRED,
                    'Nonempty list elements are required')
        if error_context.has_errors():
            return None
        return value

# Only works for lists of scalars
class Unique(Validator):
    '''Usage: Unique()
    [1, 2, 3] --> Valid
    [1, 2, 1] --> Invalid
    Only works for lists of scalars (or any hashable type).
    '''

    documentation = 'Unique values are required'

    def validate(self, value, error_context, context):
        items_seen = set()
        for i, item in enumerate(value or []):
            if item in items_seen:
                error_context.extend(index=i).add_error(
                    CommonErrorCodes.DUPLICATE_VALUE,
                    'Duplicate value found: "%s"' % item)
            items_seen.add(item)
        if error_context.has_errors():
            return None
        return value

class UniqueFields(Validator):
    '''Usage: UniqueFields('id')
    [{'id': 1}, {'id': 2}] --> Valid
    [{'id': 1}, {'id': 1}] --> Invalid
    Works only on lists of objects.
    '''

    def __init__(self, field_name):
        self.field_name = field_name

    def get_documentation(self):
        return 'Unique values for "%s" are required' % self.field_name

    def validate(self, value, error_context, context):
        item_values_seen = set()
        for i, item in enumerate(value or []):
            if item:
                item_value = getattr(item, self.field_name, None)
                if item_value is not None and item_value in item_values_seen:
                    error_context.extend(index=i).extend(field=self.field_name) \
                        .add_error(CommonErrorCodes.DUPLICATE_VALUE,
                            'Duplicate value found: "%s"' % item_value)
                item_values_seen.add(item_value)
        if error_context.has_errors():
            return None
        return value

class Range(Validator):
    '''Usage: Range(min_=1, max_=10)'''

    def __init__(self, min_=None, max_=None):
        if min_ is None and max_ is None:
            raise Exception('Must specify at least a min or max')
        self.min = min_
        self.max = max_

    def get_documentation(self):
        if self.min and self.max:
            return 'Value must be between %s and %s (inclusive)' % (self.min, self.max)
        elif self.min:
            return 'Value must be greater than or equal to %s' % self.min
        else:
            return 'Value must be less than or equal to %s' % self.max

    def validate(self, value, error_context, context):
        if value is None:
            return value
        if self.min is not None and value < self.min:
            error_context.add_error(CommonErrorCodes.VALUE_NOT_IN_RANGE, 'Value %s is less than %s' % (value, self.min))
            return None
        if self.max is not None and value > self.max:
            error_context.add_error(CommonErrorCodes.VALUE_NOT_IN_RANGE, 'Value %s is greater than %s' % (value, self.max))
            return None
        return value

class ExactlyOneNonempty(Validator):
    '''Usage: ExactlyOneNonempty('ids', 'user_ids')
    {'ids': [1, 2, 3], 'user_ids': []} --> Valid
    {'ids': None, 'user_ids': [3]} --> Valid
    {'ids': [1], 'user_ids': [3]} --> Invalid
    {'ids': None, 'user_ids': None} --> Invalid
    When constructing, specify all field names including that of the field
    this validator is being created for.
    '''

    def __init__(self, *field_names):
        self.field_names = field_names

    def get_documentation(self):
        return 'Exactly one of %s must be nonempty' % ', '.join(self.field_names)

    def validate(self, value, error_context, context):
        num_nonempty_fields = 0
        for field_name in self.field_names:
            if context.parent.get(field_name) not in EMPTY_VALUES:
                num_nonempty_fields += 1
        if num_nonempty_fields == 0:
            error_context.add_error(CommonErrorCodes.REQUIRED,
                'Exactly one of %s must be nonempty' % ', '.join(self.field_names))
            return None
        elif num_nonempty_fields > 1:
            error_context.add_error(CommonErrorCodes.AMBIGUOUS,
                'Exactly one of %s must be nonempty' % ', '.join(self.field_names))
            return None
        return value

class AtMostOneNonempty(Validator):
    '''Usage: AtMostOneNonempty('ids', 'user_ids')
    {'ids': [1, 2, 3], 'user_ids': []} --> Valid
    {'ids': None, 'user_ids': [3]} --> Valid
    {'ids': [1], 'user_ids': [3]} --> Invalid
    {'ids': None, 'user_ids': None} --> Valid
    When constructing, specify all field names including that of the field
    this validator is being created for.
    '''

    def __init__(self, *field_names):
        self.field_names = field_names

    def get_documentation(self):
        return 'At most one of %s must be nonempty' % ', '.join(self.field_names)

    def validate(self, value, error_context, context):
        num_nonempty_fields = 0
        for field_name in self.field_names:
            if context.parent.get(field_name) not in EMPTY_VALUES:
                num_nonempty_fields += 1
        if num_nonempty_fields > 1:
            error_context.add_error(CommonErrorCodes.AMBIGUOUS,
                'At most one of %s must be nonempty' % ', '.join(self.field_names))
            return None
        return value
