import unittest

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

class ValidationTest(unittest.TestCase):
    def assertHasError(self, errors, error_code, path):
        for error in errors:
            if error.code == error_code and error.path == path:
                return
        self.fail('Error with code %s and path %s not found' % (error_code, path))

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


if __name__ == '__main__':
    unittest.main()
