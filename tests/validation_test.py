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


class ValidationTest(unittest.TestCase, ExtraAssertionsMixin):
    def test_simple_valid(self):
        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json(None, error_context=ec)
        self.assertIsNotNone(m)
        self.assertEqual(None, m.fstring)
        self.assertFalse(ec.has_errors())

        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json({'fstring': None}, error_context=ec)
        self.assertIsNotNone(m)
        self.assertEqual(None, m.fstring)
        self.assertFalse(ec.has_errors())

        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json({'fstring': 'foo'}, error_context=ec)
        self.assertIsNotNone(m)
        self.assertEqual('foo', m.fstring)
        self.assertFalse(ec.has_errors())

    def test_simple_invalid(self):
        ec = apilib.ErrorContext()
        m = SimpleValidationModel.from_json({'fstring': 'EvIL'}, error_context=ec)
        self.assertIsNone(m)
        self.assertTrue(ec.has_errors())
        errors = ec.all_errors()
        self.assertEqual(1, len(errors))
        self.assertEqual('EVIL_VALUE',errors[0].code)
        self.assertEqual('fstring', errors[0].path)
        self.assertEqual('An evil value was found', errors[0].msg)

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


if __name__ == '__main__':
    unittest.main()
