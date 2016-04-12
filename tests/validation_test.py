import unittest

import apilib

class NotEvilValidator(apilib.Validator):
    def validate(self, value, error_context, context):
        if value and value.lower() == 'evil':
            error_context.add_error('EVIL_VALUE', 'An evil value was found')
            return None
        return value

class SimpleValidationModel(apilib.Model):
    fstring = apilib.Field(apilib.String(), validators=[NotEvilValidator()])

class ValidationTest(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
