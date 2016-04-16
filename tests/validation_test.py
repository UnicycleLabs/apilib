import datetime
import unittest

from dateutil import tz

import apilib

apilib.model.ID_ENCRYPTION_KEY = 'test'

class NotEvilValidator(apilib.Validator):
    def validate(self, value, error_context, context):
        if value and value.lower() == 'evil':
            error_context.add_error('EVIL_VALUE', 'An evil value was found')
            return None
        return value

class SimpleValidationModel(apilib.Model):
    fstring = apilib.Field(apilib.String(), validators=[NotEvilValidator()])

class SimpleChild(apilib.Model):
    fstring = apilib.Field(apilib.String())

class AllBasicTypesModel(apilib.Model):
    fstring = apilib.Field(apilib.String())
    fint = apilib.Field(apilib.Integer())
    ffloat = apilib.Field(apilib.Float())
    fbool = apilib.Field(apilib.Boolean())
    fdate = apilib.Field(apilib.Date())
    fdatetime = apilib.Field(apilib.DateTime())
    fdecimal = apilib.Field(apilib.Decimal())
    fenum = apilib.Field(apilib.Enum(['Jerry', 'George']))
    fid = apilib.Field(apilib.EncryptedId())

class ExtraAssertionsMixin(object):
    def assertHasError(self, errors, error_code, path):
        for error in errors:
            if error.code == error_code and error.path == path:
                return
        self.fail('Error with code %s and path %s not found' % (error_code, path))


class SimpleValidationTest(unittest.TestCase, ExtraAssertionsMixin):
    def test_simple_valid(self):
        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json(None, ec, apilib.ValidationContext())
        self.assertIsNone(m)
        self.assertFalse(ec.has_errors())

        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json({'fstring': None}, ec, apilib.ValidationContext())
        self.assertIsNotNone(m)
        self.assertEqual(None, m.fstring)
        self.assertFalse(ec.has_errors())

        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json({'fstring': 'foo'}, ec, apilib.ValidationContext())
        self.assertIsNotNone(m)
        self.assertEqual('foo', m.fstring)
        self.assertFalse(ec.has_errors())

    def test_simple_invalid(self):
        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json({'fstring': 'EvIL'}, ec, apilib.ValidationContext())
        self.assertIsNone(m)
        self.assertTrue(ec.has_errors())
        errors = ec.all_errors()
        self.assertEqual(1, len(errors))
        self.assertEqual('EVIL_VALUE',errors[0].code)
        self.assertEqual('fstring', errors[0].path)
        self.assertEqual('An evil value was found', errors[0].msg)

    def test_no_validation_if_no_context(self):
        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json({'fstring': 'EvIL'}, ec, )
        self.assertIsNotNone(m)
        self.assertEqual('EvIL', m.fstring)
        self.assertFalse(ec.has_errors())

    def test_types_are_enforced(self):
        with self.assertRaises(apilib.DeserializationError) as e:
            AllBasicTypesModel.from_json(dict(fstring=123, fint='1', ffloat='1.0', fbool='True',
                fdate=123, fdatetime=345, fdecimal=0.1, fenum=1, fid=5))
        self.assertEqual(9, len(e.exception.errors))
        errors = e.exception.errors
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'fstring')
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'fint')
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'ffloat')
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'fbool')
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'fdate')
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'fdatetime')
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'fdecimal')
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'fenum')
        self.assertHasError(errors, apilib.CommonErrorCodes.INVALID_TYPE, 'fid')

class DateTimeValidationTest(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        fdate = apilib.Field(apilib.Date())
        fdatetime = apilib.Field(apilib.DateTime())

    def test_invalid(self):
        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdate='20160202'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdate')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdate='January 1 2012'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdate')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdate='2016-0202'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdate')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdate='01/12/2018'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdate')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdate='2016-20-03'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdate')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdate='2016-04-35'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdate')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2016-04-12T15:37:37.739018'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdatetime')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2016-04-12 15:37:37.739018+00:00'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdatetime')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2016-04-12T15:37+00:00'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdatetime')

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2016-04-12T15:37:00.+00:00'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdatetime')

        m = self.Model.from_json(dict(fdatetime='2023-12-12T15:37:37+06:00'), ec)
        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2023-1-12T15:37:37+06:00'), ec)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertHasError(ec.all_errors(), apilib.CommonErrorCodes.INVALID_VALUE, 'fdatetime')

    def test_valid(self):
        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdate='2016-04-03'), ec)
        self.assertFalse(ec.has_errors())
        self.assertEqual(datetime.date(2016, 4, 3), m.fdate)

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdate='2016-4-5'), ec)
        self.assertFalse(ec.has_errors())
        self.assertEqual(datetime.date(2016, 4, 5), m.fdate)

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2016-04-12T15:37:37.739018+00:00'), ec)
        self.assertFalse(ec.has_errors())
        self.assertEqual(datetime.datetime(2016, 4, 12, 15, 37, 37, 739018, tzinfo=tz.tzutc()), m.fdatetime)

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2016-04-12T15:37:37+00:00'), ec)
        self.assertFalse(ec.has_errors())
        self.assertEqual(datetime.datetime(2016, 4, 12, 15, 37, 37, tzinfo=tz.tzutc()), m.fdatetime)

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2016-04-12T15:37:37-07:00'), ec)
        self.assertFalse(ec.has_errors())
        self.assertEqual(datetime.datetime(2016, 4, 12, 15, 37, 37, tzinfo=tz.tzoffset(None, -25200)), m.fdatetime)

        ec = apilib.ErrorContext()
        m = self.Model.from_json(dict(fdatetime='2023-12-12T15:37:37+06:00'), ec)
        self.assertFalse(ec.has_errors())
        self.assertEqual(datetime.datetime(2023, 12, 12, 15, 37, 37, tzinfo=tz.tzoffset(None, 21600)), m.fdatetime)

class ErrorFieldTestChild(apilib.Model):
    lstring = apilib.Field(apilib.ListType(apilib.String()))
    fint = apilib.Field(apilib.Integer())

class ErrorFieldTestParent(apilib.Model):
    fchild = apilib.Field(apilib.ModelType(ErrorFieldTestChild))
    lchild = apilib.Field(apilib.ListType(ErrorFieldTestChild))
    dchild = apilib.Field(apilib.DictType(ErrorFieldTestChild))

class ErrorFieldPathTest(unittest.TestCase, ExtraAssertionsMixin):
    def test_error_field_paths(self):
        ec = apilib.ErrorContext()
        m = ErrorFieldTestParent.from_json({
            'fchild': {'lstring': [None, None, -1], 'fint': 'invalid'},
            'lchild': [None, {'lstring': [None, None, None, -1], 'fint': 'invalid'}],
            'dchild': {'a': {'lstring': [-1], 'fint': 'invalid'}},
            }, ec)
        self.assertIsNone(m)
        errors = ec.all_errors()
        self.assertEqual(6, len(errors))
        self.assertHasError(errors, 'INVALID_TYPE', 'fchild.lstring[2]')
        self.assertHasError(errors, 'INVALID_TYPE', 'fchild.fint')
        self.assertHasError(errors, 'INVALID_TYPE', 'lchild[1].lstring[3]')
        self.assertHasError(errors, 'INVALID_TYPE', 'lchild[1].fint')
        self.assertHasError(errors, 'INVALID_TYPE', 'dchild["a"].lstring[0]')
        self.assertHasError(errors, 'INVALID_TYPE', 'dchild["a"].fint')

class TestRequiredStringField(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        fstring = apilib.Field(apilib.String(), required=True)

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def test_absent(self):
        m, errors = self.run_test({})
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, method='insert')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, method='update', operator='ADD')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, service='service', method='update', operator='ADD')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({'fstring': None})
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({'fstring': None}, method='insert')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({'fstring': None}, method='update', operator='ADD')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({'fstring': None}, service='service', method='update', operator='ADD')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({'fstring': ''})
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({'fstring': ''}, method='insert')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({'fstring': ''}, method='update', operator='ADD')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({'fstring': ''}, service='service', method='update', operator='ADD')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

    def test_present(self):
        m, errors = self.run_test({'fstring': 'foo'})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, method='insert')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, method='update', operator='ADD')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, service='service', method='update', operator='ADD')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)


class TestMethodSpecificRequiredStringField(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        fstring = apilib.Field(apilib.String(), required=['update/SET', 'service.foo', 'bar'])

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def test_absent_and_invalid(self):
        m, errors = self.run_test({}, method='update', operator='SET')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, service='service', method='update', operator='SET')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, service='service', method='foo')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, service='service', method='foo', operator='SET')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, method='bar')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, method='bar', operator='SET')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

        m, errors = self.run_test({}, service='service', method='bar', operator='SET')
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fstring')

    def test_absent_but_valid(self):
        m, errors = self.run_test({'fstring': None})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': None}, method='update', operator='ADD')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': None}, method='insert', operator='SET')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': None}, method='foo')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': None}, service='service', method='blah')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

    def test_present_and_valid(self):
        m, errors = self.run_test({'fstring': 'foo'}, method='update', operator='SET')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, service='service', method='update', operator='SET')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, service='service', method='foo')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, service='service', method='foo', operator='SET')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, method='bar')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, method='bar', operator='SET')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, service='service', method='bar', operator='SET')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, method='update', operator='ADD')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, method='insert', operator='SET')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, method='foo')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fstring': 'foo'}, service='service', method='blah')
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

class TestRequiredNumericFields(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        fint = apilib.Field(apilib.Integer(), required=True)
        ffloat = apilib.Field(apilib.Float(), required=True)

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def test_absent_and_invalid(self):
        m, errors = self.run_test({})
        self.assertIsNone(m)
        self.assertEqual(2, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fint')
        self.assertHasError(errors, 'REQUIRED', 'ffloat')

        m, errors = self.run_test({'fint': None, 'ffloat': None})
        self.assertIsNone(m)
        self.assertEqual(2, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fint')
        self.assertHasError(errors, 'REQUIRED', 'ffloat')

    def test_present_and_valid(self):
        m, errors = self.run_test({'fint': 0, 'ffloat': 0.0})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fint': 0, 'ffloat': 0})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fint': 10101, 'ffloat': -10.1})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

class TestRequiredBoolField(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        fbool = apilib.Field(apilib.Boolean(), required=True)

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def test_absent_and_invalid(self):
        m, errors = self.run_test({})
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fbool')

        m, errors = self.run_test({'fbool': None})
        self.assertIsNone(m)
        self.assertEqual(1, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fbool')

    def test_present_and_valid(self):
        m, errors = self.run_test({'fbool': False})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

        m, errors = self.run_test({'fbool': True})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

class TestRequiredListAndDictFields(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        lstring = apilib.Field(apilib.ListType(apilib.String()), required=True)
        dstring = apilib.Field(apilib.DictType(apilib.String()), required=True)

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def test_absent_and_invalid(self):
        m, errors = self.run_test({})
        self.assertIsNone(m)
        self.assertEqual(2, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'lstring')
        self.assertHasError(errors, 'REQUIRED', 'dstring')

        m, errors = self.run_test({'lstring': None, 'dstring': None})
        self.assertIsNone(m)
        self.assertEqual(2, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'lstring')
        self.assertHasError(errors, 'REQUIRED', 'dstring')

        m, errors = self.run_test({'lstring': [], 'dstring': {}})
        self.assertIsNone(m)
        self.assertEqual(2, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'lstring')
        self.assertHasError(errors, 'REQUIRED', 'dstring')

    def test_present_and_valid(self):
        m, errors = self.run_test({'lstring': ['a'], 'dstring': {'foo': 'bar'}})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

class TestRequiredModelFields(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        fchild = apilib.Field(apilib.ModelType(SimpleChild), required=True)
        lchild = apilib.Field(apilib.ListType(SimpleChild), required=True)
        dchild = apilib.Field(apilib.DictType(SimpleChild), required=True)

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def test_absent_and_invalid(self):
        m, errors = self.run_test({})
        self.assertIsNone(m)
        self.assertEqual(3, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fchild')
        self.assertHasError(errors, 'REQUIRED', 'lchild')
        self.assertHasError(errors, 'REQUIRED', 'dchild')

        m, errors = self.run_test({'fchild': None, 'lchild': None, 'dchild': None})
        self.assertIsNone(m)
        self.assertEqual(3, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fchild')
        self.assertHasError(errors, 'REQUIRED', 'lchild')
        self.assertHasError(errors, 'REQUIRED', 'dchild')

        m, errors = self.run_test({'fchild': None, 'lchild': [], 'dchild': {}})
        self.assertIsNone(m)
        self.assertEqual(3, len(errors))
        self.assertHasError(errors, 'REQUIRED', 'fchild')
        self.assertHasError(errors, 'REQUIRED', 'lchild')
        self.assertHasError(errors, 'REQUIRED', 'dchild')

    def test_present_and_valid(self):
        m, errors = self.run_test({'fchild': {}, 'lchild': [{}], 'dchild': {'foo': {}}})
        self.assertIsNotNone(m)
        self.assertEqual([], errors)

class TestReadonlyScalarFields(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        fstring = apilib.Field(apilib.String(), readonly=True)
        fint = apilib.Field(apilib.Integer(), readonly=True)
        ffloat = apilib.Field(apilib.Float(), readonly=True)
        fbool = apilib.Field(apilib.Boolean(), readonly=True)

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def assertAllNone(self, m):
        self.assertIsNotNone(m)
        self.assertIsNone(m.fstring)
        self.assertIsNone(m.fint)
        self.assertIsNone(m.ffloat)
        self.assertIsNone(m.fbool)

    def test_absent(self):
        m, errors = self.run_test({})
        self.assertEqual([], errors)
        self.assertAllNone(m)

        m, errors = self.run_test({'fstring': None, 'fint': None, 'ffloat': None, 'fbool': None})
        self.assertEqual([], errors)
        self.assertAllNone(m)

    def test_present_and_stripped(self):
        m, errors = self.run_test({'fstring': 'foo', 'fint': 100, 'ffloat': 9.9, 'fbool': True})
        self.assertEqual([], errors)
        self.assertAllNone(m)

        m, errors = self.run_test({'fstring': '', 'fint': 0, 'ffloat': 0.0, 'fbool': False})
        self.assertEqual([], errors)
        self.assertAllNone(m)

class TestReadonlyListAndDictFields(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        lstring = apilib.Field(apilib.ListType(apilib.String()), readonly=True)
        dstring = apilib.Field(apilib.DictType(apilib.String()), readonly=True)

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def assertAllNone(self, m):
        self.assertIsNotNone(m)
        self.assertIsNone(m.lstring)
        self.assertIsNone(m.dstring)

    def test_absent(self):
        m, errors = self.run_test({})
        self.assertEqual([], errors)
        self.assertAllNone(m)

        m, errors = self.run_test({'lstring': None, 'dstring': None})
        self.assertEqual([], errors)
        self.assertAllNone(m)

        m, errors = self.run_test({'lstring': [], 'dstring': {}})
        self.assertEqual([], errors)
        self.assertAllNone(m)

    def test_present_and_stripped(self):
        m, errors = self.run_test({'lstring': ['a'], 'dstring': {'foo': 'bar'}})
        self.assertEqual([], errors)
        self.assertAllNone(m)

class TestReadonlyModelFields(unittest.TestCase, ExtraAssertionsMixin):
    class Model(apilib.Model):
        fchild = apilib.Field(apilib.ModelType(SimpleChild), readonly=True)
        lchild = apilib.Field(apilib.ListType(SimpleChild), readonly=True)
        dchild = apilib.Field(apilib.DictType(SimpleChild), readonly=True)

    def run_test(self, obj, service=None, method=None, operator=None):
        ec = apilib.ErrorContext()
        vc = apilib.ValidationContext(service=service, method=method, operator=operator)
        m = self.Model.from_json(obj, ec, vc)
        return m, ec.all_errors()

    def assertAllNone(self, m):
        self.assertIsNotNone(m)
        self.assertIsNone(m.fchild)
        self.assertIsNone(m.lchild)
        self.assertIsNone(m.dchild)

    def test_absent(self):
        m, errors = self.run_test({})
        self.assertEqual([], errors)
        self.assertAllNone(m)

        m, errors = self.run_test({'fchild': None, 'lchild': None, 'dchild': None})
        self.assertEqual([], errors)
        self.assertAllNone(m)

    def test_present_and_stripped(self):
        m, errors = self.run_test({'fchild': {}, 'lchild': [], 'dchild': {}})
        self.assertEqual([], errors)
        self.assertAllNone(m)

        m, errors = self.run_test({'fchild': {'fstring': 'a'}, 'lchild': [{'fstring': 'b'}], 'dchild': {'foo': {'fstring': 'c'}}})
        self.assertEqual([], errors)
        self.assertAllNone(m)


if __name__ == '__main__':
    unittest.main()
