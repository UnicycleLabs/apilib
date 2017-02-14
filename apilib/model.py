import datetime
import decimal
import inspect
import json
import re
import threading

from dateutil import parser as dateutil_parser

try:
    import hashids
except ImportError:
    hashids = None

from .validation import CommonErrorCodes
from .validation import ErrorContext
from . import exceptions
from . import validators as vals

ID_ENCRYPTION_KEY = None  # Set this to encrypt ids
ID_HASHER = None

def _create_id_hasher():
    global ID_HASHER
    if not ID_ENCRYPTION_KEY:
        raise exceptions.ConfigurationRequired('You must set apilib.ID_ENCRYPTION_KEY prior to using EncryptedId fields')
    ID_HASHER = hashids.Hashids(salt=ID_ENCRYPTION_KEY, min_length=8)

_field_lock = threading.Lock()

class Model(object):
    def __init__(self, **kwargs):
        self._data = {}
        self._populate_fields()
        for key, value in kwargs.iteritems():
            if key not in self._field_name_to_field:
                raise exceptions.UnknownFieldException('Unknown field "%s"' % key)
            setattr(self, key, value)

    def to_json(self):
        return {key: self._field_name_to_field[key].to_json(value) for key, value in self._data.iteritems()}

    def to_json_str(self):
        return json.dumps(self.to_json())

    @classmethod
    def from_json(cls, obj, error_context=None, context=None):
        cls._populate_fields()
        if obj is None:
            return None

        kwargs = {}
        is_root = not error_context
        error_context = error_context or ErrorContext()
        context = cls.make_parent_context(obj, context) if context else None
        for key, field in cls._field_name_to_field.iteritems():
            kwargs[key] = field.from_json(obj.get(key), error_context.extend(field=key), context)
        for key in obj.iterkeys():
            if key not in cls._field_name_to_field:
                error_context.extend(field=key).add_error(CommonErrorCodes.UNKNOWN_FIELD, 'Unknown field "%s"' % key)
        if error_context.has_errors():
            if is_root:
                raise exceptions.DeserializationError(error_context.all_errors())
            return None
        return cls(**kwargs)

    @classmethod
    def make_parent_context(cls, obj, context):
        return context.for_parent(obj)

    @classmethod
    def from_json_str(cls, json_str):
        return cls.from_json(json.loads(json_str))

    @classmethod
    def _populate_fields(cls):
        # Check cls.__dict__ instead of calling hasattr, because we only
        # want to check if the variable exists on the class itself
        # and not any of its parent classes.
        try:
            # In a multi-threaded environment, different threads can try to build
            # the field name dict at the same time and corrupt it.
            _field_lock.acquire()
            if '_field_to_attr_name' not in cls.__dict__:
                cls._field_to_attr_name = {}
                cls._field_name_to_field = {}
                for attr_name, attr in inspect.getmembers(cls):
                    if attr and isinstance(attr, Field):
                        cls._field_to_attr_name[attr] = attr_name
                        cls._field_name_to_field[attr_name] = attr
                        attr._name = attr_name
        finally:
            _field_lock.release()

    def __str__(self):
        return self.to_string()

    def to_string(self, indent=''):
        parts = ['<%s: {' % type(self).__name__]
        for key in sorted(self._data.iterkeys()):
            formatted_value = self._field_name_to_field[key].to_string(self._data[key], indent)
            parts.append('  %s%s: %s,' % (indent, key, formatted_value))
        parts.append('%s}>' % indent)
        return '\n'.join(parts)

class Field(object):
    def __init__(self, field_type, validators=(), required=None, readonly=None):
        self._type = field_type
        # Will be populated when the model is instantiated
        self._name = None
        self._validators = self._implicit_validators(required, readonly) + list(validators or [])

    def to_json(self, value):
        return self._type.to_json(value)

    def from_json(self, value, error_context, context=None):
        parsed_value = self._type.from_json(value, error_context, context)
        if error_context.has_errors():
            return None
        if context:
            return self._validate(parsed_value, error_context, context)
        return parsed_value

    def __get__(self, instance, type=None):
        if instance:
            return instance._data.get(self._name)
        else:
            return self

    def __set__(self, instance, value):
        instance._data[self._name] = self._type.normalize(value)

    def to_string(self, value, indent):
        return self._type.to_string(value, indent)

    def _validate(self, value, error_context, context=None):
        for validator in self._validators:
            value = validator.validate(value, error_context, context)
            if error_context.has_errors():
                return None
        return value

    def _implicit_validators(self, required, readonly):
        validators = []
        if required:
            validators.append(vals.Required(required))
        if readonly:
            validators.append(vals.Readonly(readonly))
        return validators

class FieldType(object):
    type_name = None
    json_type = None
    description = None

    def to_json(self, value):
        return value

    def from_json(self, value, error_context, context=None):
        return value

    def normalize(self, value):
        return value

    # Only for documentation

    def get_type_name(self):
        return self.json_type

    def get_json_type(self):
        return self.json_type

    def get_description(self):
        return self.description

    def to_string(self, value, indent):
        return unicode(value)

def _validate_types(value, types, error_context, type_message):
    if value is not None and type(value) not in types:
        error_context.add_error(
            CommonErrorCodes.INVALID_TYPE,
            'Unexpected type %s, expected %s' % (type(value).__name__, type_message))
        return False
    return True

class String(FieldType):
    type_name = 'string'
    json_type = 'string'

    def to_json(self, value):
        return unicode(value) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if _validate_types(value, (str, unicode), error_context, self.type_name):
            return unicode(value) if value is not None else None
        return None

    def to_string(self, value, indent):
        return (u"'%s'" % value.replace("'", "\\'")) if value is not None else unicode(None)

class Bytes(FieldType):
    type_name = 'bytes'
    json_type = 'string'

    def to_json(self, value):
        return bytes(value) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if _validate_types(value, (str, bytes, bytearray), error_context, self.type_name):
            return bytes(value) if value is not None else None
        return None

    def to_string(self, value, indent):
        if value is None:
            return unicode(None)
        try:
            unicode_value = unicode(value)
        except UnicodeDecodeError:
            return u'<...bytes...>'
        display_value = unicode_value if len(unicode_value) < 100 else unicode_value[:100] + '...'
        return u"'%s'" % display_value.replace("'", "\\'")

class Integer(FieldType):
    type_name = 'integer'
    json_type = 'integer'

    def to_json(self, value):
        return int(value) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if _validate_types(value, (int, long), error_context, self.type_name):
            return int(value) if value is not None else None
        return None

class Float(FieldType):
    type_name = 'float'
    json_type = 'float'

    def to_json(self, value):
        return float(value) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if _validate_types(value, (float, int, long), error_context, self.type_name):
            return float(value) if value is not None else None
        return None

class Boolean(FieldType):
    type_name = 'boolean'
    json_type = 'boolean'

    def to_json(self, value):
        return bool(value) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if _validate_types(value, (bool, int), error_context, self.type_name):
            return bool(value) if value is not None else None
        return None

class ModelType(FieldType):
    json_type = 'object'

    def __init__(self, model_class):
        self.model_class = model_class

    def to_json(self, value):
        return value.to_json() if value is not None else None

    def from_json(self, value, error_context, context=None):
        return self.model_class.from_json(value, error_context, context) if value is not None else None

    def get_type_name(self):
        return 'object(%s)' % self.model_class.__name__

    def to_string(self, value, indent):
        return value.to_string(indent + '  ') if value is not None else unicode(None)

class ListType(FieldType):
    json_type = 'list'

    def __init__(self, field_type_or_model_class):
        if inspect.isclass(field_type_or_model_class) and issubclass(field_type_or_model_class, Model):
            self._type = ModelType(field_type_or_model_class)
        else:
            self._type = field_type_or_model_class

    def to_json(self, value):
        if value is None:
            return None
        return [self._type.to_json(item) for item in value]

    def from_json(self, value, error_context, context=None):
        if value is None:
            return None
        value = [self._type.from_json(item, error_context.extend(index=i), context) for i, item in enumerate(value)]
        return value if not error_context.has_errors() else None

    def normalize(self, value):
        return list(value) if value is not None else None

    def get_type_name(self):
        return 'list(%s)' % self._type.get_type_name()

    def to_string(self, value, indent):
        if value is None:
            return unicode(None)
        new_indent = indent + '    '
        parts = ['['] + ['%s%s,' % (new_indent, self._type.to_string(item, new_indent)) for item in value] + [new_indent + ']']
        return '\n'.join(parts)

class DictType(FieldType):
    json_type = 'object'

    def __init__(self, field_type_or_model_class):
        if inspect.isclass(field_type_or_model_class) and issubclass(field_type_or_model_class, Model):
            self._type = ModelType(field_type_or_model_class)
        else:
            self._type = field_type_or_model_class

    def to_json(self, value):
        if value is None:
            return None
        return {k: self._type.to_json(v) for k, v in value.iteritems()}

    def from_json(self, value, error_context, context=None):
        if value is None:
            return None
        if not isinstance(value, dict):
            error_context.add_error(CommonErrorCodes.INVALID_TYPE, 'Value %s is not a dict' % value)
            return None
        value = {k: self._type.from_json(v, error_context.extend(key=k), context) for k,v in value.iteritems()}
        return value if not error_context.has_errors() else None

    def normalize(self, value):
        return dict(value) if value is not None else None

    def get_type_name(self):
        return 'dict(%s)' % self._type.get_type_name()

    def to_string(self, value, indent):
        if value is None:
            return unicode(None)
        new_indent = indent + '    '
        parts = ['{'] + ['%s%s: %s,' % (new_indent, k, self._type.to_string(v, new_indent)) for k, v in value.iteritems()] + [new_indent + '}']
        return '\n'.join(parts)

class DateTime(FieldType):
    type_name = 'datetime'
    json_type = 'string'
    description = 'A datetime with time zone in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM)'

    ISO_8601_RE = re.compile('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?((\+|-)\d{2}:\d{2})?$')

    def to_json(self, value):
        return unicode(value.isoformat()) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if value is None:
            return None
        if type(value) not in (str, unicode):
            error_context.add_error(CommonErrorCodes.INVALID_TYPE,
                'Value %s is invalid for datetime. Value must be a string in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM)' % value)
            return None
        if self.ISO_8601_RE.match(value):
            try:
                dt = dateutil_parser.parse(unicode(value))
            except ValueError:
                dt = None
        else:
            dt = None
        if not dt:
            error_context.add_error(
                CommonErrorCodes.INVALID_VALUE,
               'Unable to parse "%s" as a datetime. Value must be a string in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM)' % value)
            return None
        return dt

class Date(FieldType):
    type_name = 'date'
    json_type = 'string'
    description = 'A date in ISO 8601 format (YYYY-MM-DD)'

    def to_json(self, value):
        return unicode(value.isoformat()) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if value is None:
            return None
        if type(value) not in (str, unicode):
            error_context.add_error(CommonErrorCodes.INVALID_TYPE,
                'Value %s is invalid for date. Value must be a string in ISO 8601 format (YYYY-MM-DD)' % value)
            return None
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            pass
        error_context.add_error(
            CommonErrorCodes.INVALID_VALUE,
           'Unable to parse "%s" as a date. Value must be a string in ISO 8601 format (YYYY-MM-DD)' % value)
        return None

class Decimal(FieldType):
    type_name = 'decimal'
    json_type = 'string'
    description = 'A fixed-point decimal number'

    def to_json(self, value):
        return unicode(value) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if value is not None:
            if type(value) not in (str, unicode):
                error_context.add_error(
                    CommonErrorCodes.INVALID_TYPE,
                   'Decimal values must be passed as a string')
                return None

            try:
                return decimal.Decimal(value)
            except (TypeError, decimal.InvalidOperation):
                error_context.add_error(
                    CommonErrorCodes.INVALID_VALUE,
                   'Unable to parse "%s" as a decimal number' % value)
        return None

class Enum(FieldType):
    json_type = 'string'

    def __init__(self, values):
        self.values = set(values)

    def to_json(self, value):
        return unicode(value) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if value is None:
            return None
        if type(value) not in (str, unicode):
            error_context.add_error(
                CommonErrorCodes.INVALID_TYPE,
                'Value %s is invalid for enums. Enum values must be passed as strings' % value)
            return None
        if value not in self.values:
            error_context.add_error(
                CommonErrorCodes.INVALID_VALUE,
               '"%s" is not a valid enum for this type. Valid values are %s' % (value, ', '.join(sorted(self.values))))
            return None
        return value

    def get_type_name(self):
        return 'enum(%s)' % ', '.join(sorted(self.values))

    def to_string(self, value, indent):
        return unicode(value)

class EnumValues(object):
    '''A simple class that exposes a values() method that gets all string scalars defined at class level.

    Usage:

    class MyEnum(EnumValues):
        FOO = 'foo'
        BAR = 'bar'

    class MyModel(Model):
        enum_field = Field(Enum(MyEnum.values()))
    '''

    @classmethod
    def values(cls):
        if '_values' not in cls.__dict__:
            values = []
            for k, v in cls.__dict__.iteritems():
                if not k.startswith('_') and isinstance(v, basestring):
                    values.append(v)
            cls._values = sorted(values)
        return cls._values

class EncryptedId(FieldType):
    type_name = 'id'
    json_type = 'string'
    description = 'An entity id'

    def __init__(self):
        if not hashids:
            raise exceptions.ModuleRequired('You must install the hashids module in order to use EncryptedId fields')
        if not ID_HASHER:
            _create_id_hasher()

    def to_json(self, value):
        return ID_HASHER.encode(value) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if value is None:
            return None
        if type(value) not in (str, unicode):
            error_context.add_error(CommonErrorCodes.INVALID_TYPE, 'Ids must be passed as strings')
            return None
        # Unclear why this doesn't work with unicode values,
        # must coerce it to be a string.
        ids = ID_HASHER.decode(str(value))
        if not ids or len(ids) > 1:
            error_context.add_error(CommonErrorCodes.INVALID_VALUE, '"%s" is not a valid id' % value)
            return None
        return ids[0]

class AnyPrimitive(FieldType):
    type_name = 'any'
    json_type = 'any'
    description = 'Any primitive type (int, float, boolean, string, list, object) and compositions thereof. Used for mixed-type objects, like an arbitrary dict'

    def to_json(self, value):
        return value

    def from_json(self, value, error_context, context=None):
        return value

    def to_string(self, value, indent):
        return unicode(value)
