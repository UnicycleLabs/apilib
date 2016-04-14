import decimal
import unittest

import apilib

class ApiValidatorsTest(unittest.TestCase):
    def run_validator_test(self, validator, value, *error_codes):
        self.run_validator_test_for_method(validator, value, None, *error_codes)

    def run_validator_test_for_method(self, validator, value, method, *error_codes):
        error_context = apilib.ErrorContext()
        validator.validate(value, error_context, apilib.ValidationContext(method=method))
        if error_codes:
            self.assertTrue(error_context.has_errors())
            for error_code in error_codes:
                self.assertHasErrorCode(error_code, error_context)
        else:
            self.assertFalse(error_context.has_errors())

    def run_validator_test_for_context(self, validator, value, context, *error_codes):
        error_context = apilib.ErrorContext()
        validator.validate(value, error_context, context)
        if error_codes:
            self.assertTrue(error_context.has_errors())
            for error_code in error_codes:
                self.assertHasErrorCode(error_code, error_context)
        else:
            self.assertFalse(error_context.has_errors())

    def assertHasErrorCode(self, error_code, error_context):
        for error in error_context.errors:
            if error.code == error_code:
                return
        self.fail('Error code %s not found' % error_code)

    def test_required_validator(self):
        self.run_validator_test(apilib.Required(), None, apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(), '', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(), u'', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(), [], apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(), {}, apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(), 'abc')
        self.run_validator_test(apilib.Required(), 123)
        self.run_validator_test(apilib.Required(), 0)
        self.run_validator_test(apilib.Required(), 0.0)
        self.run_validator_test(apilib.Required(), u'abc')
        self.run_validator_test(apilib.Required(), ['abc'])
        self.run_validator_test(apilib.Required(), [1, 2, 3])
        self.run_validator_test(apilib.Required(), [None])

        self.run_validator_test(apilib.Required(True), None, apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(True), '', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(True), u'', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(True), [], apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(True), {}, apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test(apilib.Required(True), 'abc')
        self.run_validator_test(apilib.Required(True), 123)
        self.run_validator_test(apilib.Required(True), 0)
        self.run_validator_test(apilib.Required(True), 0.0)
        self.run_validator_test(apilib.Required(True), u'abc')
        self.run_validator_test(apilib.Required(True), ['abc'])
        self.run_validator_test(apilib.Required(True), [1, 2, 3])
        self.run_validator_test(apilib.Required(True), [None])

        self.run_validator_test_for_method(apilib.Required(['insert']), None, 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required(['insert']), '', 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required(['insert']), [], 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required(['insert']), {}, 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required(['insert']), None, 'update')
        self.run_validator_test_for_method(apilib.Required(['insert']), [], 'update')
        self.run_validator_test_for_method(apilib.Required(['insert']), {}, 'update')
        self.run_validator_test_for_method(apilib.Required(['insert']), 123, 'insert')
        self.run_validator_test_for_method(apilib.Required(['insert']), 'abc', 'insert')
        self.run_validator_test_for_method(apilib.Required(['insert']), [1], 'insert')

        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), None, 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), '', 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), [], 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), {}, 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), None, 'update')
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), [], 'update')
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), {}, 'update')
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), 123, 'insert')
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), 'abc', 'insert')
        self.run_validator_test_for_method(apilib.Required(['get', 'insert']), [1], 'insert')

        self.run_validator_test_for_method(apilib.Required('insert'), None, 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required('insert'), '', 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required('insert'), [], 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required('insert'), {}, 'insert', apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(apilib.Required('insert'), None, 'update')
        self.run_validator_test_for_method(apilib.Required('insert'), [], 'update')
        self.run_validator_test_for_method(apilib.Required('insert'), {}, 'update')
        self.run_validator_test_for_method(apilib.Required('insert'), 123, 'insert')
        self.run_validator_test_for_method(apilib.Required('insert'), 'abc', 'insert')
        self.run_validator_test_for_method(apilib.Required('insert'), [1], 'insert')

        VC = apilib.ValidationContext
        self.run_validator_test_for_context(apilib.Required('insert/ADD'), None, VC(method='insert', operator='ADD'), apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_context(apilib.Required('insert/ADD'), None, VC(method='insert', operator='UPDATE'))
        self.run_validator_test_for_context(apilib.Required('insert/ADD'), None, VC(method='insert', operator=None))
        self.run_validator_test_for_context(apilib.Required('fooservice.insert/ADD'), None, VC(service='fooservice', method='insert', operator='ADD'), apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_context(apilib.Required('fooservice.insert/ADD'), None, VC(service=None, method='insert', operator='ADD'))
        self.run_validator_test_for_context(apilib.Required('fooservice.insert'), None, VC(service='fooservice', method='insert', operator='ADD'), apilib.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_context(apilib.Required('fooservice.insert'), None, VC(service='fooservice', method='insert'), apilib.CommonErrorCodes.REQUIRED)

    def test_readonly_validator(self):
        Readonly = apilib.Readonly
        VC = apilib.ValidationContext

        self.assertEqual(
            None,
            Readonly(True).validate('foo', None, VC(method='insert')))
        self.assertEqual(
            None,
            Readonly('insert').validate('foo', None, VC(method='insert')))
        self.assertEqual(
            None,
            Readonly(['insert']).validate('foo', None, VC(method='insert')))
        self.assertEqual(
            None,
            Readonly(['update', 'insert']).validate('foo', None, VC(method='insert')))
        self.assertEqual(
            None,
            Readonly(['insert']).validate('foo', None, VC(service='service', method='insert')))
        self.assertEqual(
            None,
            Readonly(['insert']).validate('foo', None, VC(service='service', method='insert', operator='ADD')))
        self.assertEqual(
            None,
            Readonly(['insert/ADD']).validate('foo', None, VC(service='service', method='insert', operator='ADD')))
        self.assertEqual(
            None,
            Readonly(['service.insert/ADD']).validate('foo', None, VC(service='service', method='insert', operator='ADD')))

        self.assertEqual(
            'foo',
            Readonly('insert').validate('foo', None, VC(method='update')))
        self.assertEqual(
            'foo',
            Readonly('insert').validate('foo', None, VC(service='service', method='update')))
        self.assertEqual(
            'foo',
            Readonly('insert').validate('foo', None, VC(service='service', method='update', operator='ADD')))
        self.assertEqual(
            'foo',
            Readonly(['service.insert/ADD']).validate('foo', None, VC(service='service', method='insert', operator='UPDATE')))
        self.assertEqual(
            'foo',
            Readonly(['service.insert/ADD']).validate('foo', None, VC(service=None, method='insert', operator='ADD')))


if __name__ == '__main__':
    unittest.main()
