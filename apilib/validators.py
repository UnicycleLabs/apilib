import decimal

from .validation import CommonErrorCodes
from .validation import MethodMatcher
from .validation import Validator

class Required(Validator):
    def __init__(self, method_spec=True):
        self.method_matcher = MethodMatcher(method_spec)

    def get_documentation(self):
        if not self.method_matcher.for_all_methods():
            return 'Value is required'
        return 'Value is required for methods: %s' % ','.join(self.method_matcher.methods())

    def validate(self, value, error_context, context):
        if value in (None, [], {}, ''):
            if self.method_matcher.matches(context.service, context.method, context.operator):
                if self.method_matcher.for_all_methods():
                    msg = 'Field is required'
                else:
                    msg = 'Field is required on method "%s"' % context.method
                error_context.add_error(CommonErrorCodes.REQUIRED, msg)
                return None
        return value

class Readonly(Validator):
    def __init__(self, method_spec=True):
        self.method_matcher = MethodMatcher(method_spec)

    def get_documentation(self):
        if not self.method_matcher.for_all_methods():
            return 'Value is read-only'
        return 'Value is read-only for methods: %s' % ','.join(self.method_matcher.methods())

    def validate(self, value, error_context, context):
        if self.method_matcher.matches(context.service, context.method, context.operator):
            return None
        return value

class NonemptyElements(Validator):
    documentation = 'Nonempty elements are required'

    def validate(self, value, error_context, context):
        for i, item in enumerate(value or []):
            if not item:
                error_context.extend_path_for_index(i).add_error(
                    CommonErrorCodes.NONEMPTY_ITEM_REQUIRED,
                    'Nonempty list elements are required')
        return value

class Unique(Validator):
    documentation = 'Unique values are required'

    def validate(self, value, error_context, context):
        items_seen = set()
        for i, item in enumerate(value or []):
            if item:
                if item in items_seen:
                    error_context.extend_path_for_index(i).add_error(
                        CommonErrorCodes.DUPLICATE_VALUE,
                        'Duplicate value found: "%s"' % item)
                items_seen.add(item)
        return value

class UniqueFields(Validator):
    def __init__(self, field_name):
        self.field_name = field_name

    def get_documentation(self):
        return 'Unique values for "%s" are required' % self.field_name

    def validate(self, value, error_context, context):
        item_values_seen = set()
        for i, item in enumerate(value or []):
            if item:
                item_value = getattr(item, self.field_name, None)
                if item_value and item_value in item_values_seen:
                    error_context.extend_path_for_index(i).extend_path_for_field(self.field_name) \
                        .add_error(CommonErrorCodes.DUPLICATE_VALUE,
                            'Duplicate value found: "%s"' % item_value)
                item_values_seen.add(item_value)
        return value

class Range(Validator):
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
        if self.max is not None and value > self.max:
            error_context.add_error(CommonErrorCodes.VALUE_NOT_IN_RANGE, 'Value %s is great than %s' % (value, self.max))
        return value

class ExactlyOneNonempty(Validator):
    # field_names should include all fields that are dependent on each
    # other including this one.
    def __init__(self, *field_names):
        self.field_names = field_names

    def get_documentation(self):
        return 'Exactly one of %s must be nonempty' % ', '.join(self.field_names)

    def validate(self, value, error_context, context):
        num_nonempty_fields = 0
        for field_name in self.field_names:
            if getattr(context.parent_model, field_name):
                num_nonempty_fields += 1
        if num_nonempty_fields == 0:
            error_context.add_error(CommonErrorCodes.REQUIRED,
                'Exactly one of %s must be nonempty' % ', '.join(self.field_names))
        elif num_nonempty_fields > 1:
            error_context.add_error(CommonErrorCodes.AMBIGUOUS,
                'Exactly one of %s must be nonempty' % ', '.join(self.field_names))
        return value

class DifferentThan(Validator):
    def __init__(self, *field_names):
        self.field_names = field_names

    def get_documentation(self):
        return 'Must not have the same value as %s' % ', '.join(self.field_names)

    def validate(self, value, error_context, context):
        if value:
            for field_name in self.field_names:
                if value == getattr(context.parent_model, field_name):
                    error_context.add_error(CommonErrorCodes.REPEATED,
                        'Must not have the same value as %s' % ', '.join(self.field_names))
        return value
