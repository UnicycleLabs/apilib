import datetime
import decimal
import inspect
import json

from dateutil import parser as dateutil_parser

try:
    import hashids
except ImportError:
    hashids = None

from .validation import CommonErrorCodes
from .validation import ErrorContext

ID_ENCRYPTION_KEY = None  # Set this to encrypt ids
ID_HASHER = None

def _create_id_hasher():
    global ID_HASHER
    if not ID_ENCRYPTION_KEY:
        raise ConfigurationRequired('You must set apilib.ID_ENCRYPTION_KEY prior to using EncryptedId fields')
    ID_HASHER = hashids.Hashids(salt=ID_ENCRYPTION_KEY, min_length=8)

class UnknownFieldException(Exception):
    pass

class ModuleRequired(Exception):
    pass

class ConfigurationRequired(Exception):
    pass

class DeserializationError(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return 'DeserializationError:\n%s' % '\n'.join(str(e) for e in self.errors)

class Model(object):
    def __init__(self, **kwargs):
        self._data = {}
        self._populate_fields()
        for key, value in kwargs.iteritems():
            if key not in self._field_name_to_field:
                raise UnknownFieldException('Unknown field "%s"' % key)
            setattr(self, key, value)

    def to_json(self):
        return {key: self._field_name_to_field[key].to_json(value) for key, value in self._data.iteritems()}

    def to_json_str(self):
        return json.dumps(self.to_json())

    @classmethod
    def from_json(cls, obj, error_context=None, context=None):
        cls._populate_fields()
        kwargs = {}
        is_root = not error_context
        error_context = error_context or ErrorContext()
        for key, value in obj.iteritems() if obj is not None else []:
            field = cls._field_name_to_field.get(key)
            if field:
                context = context.for_parent(obj) if context else None
                kwargs[key] = field.from_json(value, error_context.extend(field=key), context)
        if error_context.has_errors():
            if is_root:
                raise DeserializationError(error_context.all_errors())
            return None
        return cls(**kwargs)

    @classmethod
    def from_json_str(cls, json_str):
        return cls.from_json(json.loads(json_str))

    @classmethod
    def _populate_fields(cls):
        if not hasattr(cls, '_field_to_attr_name'):
            cls._field_to_attr_name = {}
            cls._field_name_to_field = {}
            for attr_name, attr in cls.__dict__.iteritems():
                if attr and isinstance(attr, Field):
                    cls._field_to_attr_name[attr] = attr_name
                    cls._field_name_to_field[attr_name] = attr
                    attr._name = attr_name

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
    def __init__(self, field_type, validators=()):
        self._type = field_type
        # Will be populated when the model is instantiated
        self._name = None
        self._validators = validators

    def to_json(self, value):
        return self._type.to_json(value)

    def from_json(self, value, error_context, context=None):
        value = self._type.from_json(value, error_context, context=None)
        if error_context.has_errors():
            return None
        return self._validate(value, error_context, context=None)

    def __get__(self, instance, type=None):
        if instance:
            return instance._data.get(self._name)
        else:
            return self

    def __set__(self, instance, value):
        instance._data[self._name] = value

    def to_string(self, value, indent):
        return self._type.to_string(value, indent)

    def _validate(self, value, error_context, context=None):
        for validator in self._validators:
            value = validator.validate(value, error_context, context)
            if error_context.has_errors():
                return None
        return value

class ListField(Field):
    def __init__(self, field_type_or_model_class):
        if inspect.isclass(field_type_or_model_class) and issubclass(field_type_or_model_class, Model):
            field_type = ModelFieldType(field_type_or_model_class)
        else:
            field_type = field_type_or_model_class
        super(ListField, self).__init__(field_type)

    def to_json(self, value):
        if value is None:
            return None
        return [self._type.to_json(item) for item in value]

    def from_json(self, value, error_context, context=None):
        if value is not None:
            value = [self._type.from_json(item, error_context.extend(index=i), context) for i, item in enumerate(value)]
            if error_context.has_errors():
                return None
        return self._validate(value, error_context, context)

    def __set__(self, instance, value):
        instance._data[self._name] = list(value) if value is not None else None

    def to_string(self, value, indent):
        if value is None:
            return unicode(None)
        new_indent = indent + '  '
        parts = ['['] + [new_indent + self._type.to_string(item, new_indent) for item in value] + [new_indent + ']']
        return '\n'.join(parts)

class ModelField(Field):
    def __init__(self, field_type_or_model_class):
        if inspect.isclass(field_type_or_model_class) and issubclass(field_type_or_model_class, Model):
            field_type = ModelFieldType(field_type_or_model_class)
        else:
            field_type = field_type_or_model_class
        super(ModelField, self).__init__(field_type)

    def to_json(self, value):
        return value.to_json() if value else None

    def from_json(self, value, error_context, context=None):
        value = self._type.from_json(value, error_context, context=None) if value is not None else None
        if error_context.has_errors():
            return None
        return self._validate(value, error_context, context=None)

    def to_string(self, value, indent):
        if value is None:
            return unicode(value)
        return value.to_string(indent + '  ')

class FieldType(object):
    type_name = None
    json_type = None
    description = None

    def to_json(self, value):
        return value

    def from_json(self, value, error_context, context=None):
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
            'Unexpected type %s, expected %s' % (type(value), type_message))
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

class ModelFieldType(FieldType):
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

class DateTime(FieldType):
    type_name = 'datetime'
    json_type = 'string'
    description = 'A datetime with time zone in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM)'

    def to_json(self, value):
        return unicode(value.isoformat()) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if value is None:
            return None
        if type(value) in (str, unicode):
            try:
                return dateutil_parser.parse(unicode(value))
            except ValueError:
                pass
        error_context.add_error(
            CommonErrorCodes.INVALID_VALUE,
           'Unable to parse "%s" as a datetime. Value must be in a string ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM)' % value)
        return None

class Date(FieldType):
    type_name = 'date'
    json_type = 'string'
    description = 'A date in ISO 8601 format (YYYY-MM-DD)'

    def to_json(self, value):
        return unicode(value.isoformat()) if value is not None else None

    def from_json(self, value, error_context, context=None):
        if value is None:
            return None
        if type(value) in (str, unicode):
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
        if value is not None and value not in self.values:
                error_context.add_error(
                    CommonErrorCodes.INVALID_VALUE,
                   '"%s" is not a valid enum for this type. Valid values are %s' % (value, ', '.join(sorted(self.values))))

        return value

    def get_type_name(self):
        return 'enum(%s)' % ', '.join(sorted(self.values))

    def to_string(self, value, indent):
        return unicode(value)

class EncryptedId(FieldType):
    type_name = 'id'
    json_type = 'string'
    description = 'An entity id'

    def __init__(self):
        if not hashids:
            raise ModuleRequired('You must install the hashids module in order to use EncryptedId fields')
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
