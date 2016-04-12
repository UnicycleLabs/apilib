import decimal
import unittest

import apilib

class ApiValidatorsTest(unittest.TestCase):
    def run_validator_test(self, validator, value, *error_codes):
        self.run_validator_test_for_method(validator, value, None, *error_codes)

    def run_validator_test_for_method(self, validator, value, method, *error_codes):
        error_context = apilib.ErrorContext()
        validator.validate(value, error_context, apilib.ValidationContext(method))
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

    def test_type_validators(self):
        self.run_validator_test(apilib.StringType(), '123')
        self.run_validator_test(apilib.StringType(), u'123')
        self.run_validator_test(apilib.StringType(), None)
        self.run_validator_test(apilib.StringType(), 123, apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.StringType(), [], apilib.CommonErrorCodes.INVALID_TYPE)

        self.run_validator_test(apilib.IntegerType(), 123)
        self.run_validator_test(apilib.IntegerType(), 123L)
        self.run_validator_test(apilib.IntegerType(), -9234234234)
        self.run_validator_test(apilib.IntegerType(), 0)
        self.run_validator_test(apilib.IntegerType(), 0L)
        self.run_validator_test(apilib.IntegerType(), None)
        self.run_validator_test(apilib.IntegerType(), '123', apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.IntegerType(), u'123', apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.IntegerType(), 123.0, apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.IntegerType(), '', apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.IntegerType(), [], apilib.CommonErrorCodes.INVALID_TYPE)

        self.run_validator_test(apilib.FloatType(), 1.0)
        self.run_validator_test(apilib.FloatType(), 1.25)
        self.run_validator_test(apilib.FloatType(), 0.0)
        self.run_validator_test(apilib.FloatType(), 0.1)
        self.run_validator_test(apilib.FloatType(), 123)
        self.run_validator_test(apilib.FloatType(), 123L)
        self.run_validator_test(apilib.FloatType(), -9234234234)
        self.run_validator_test(apilib.FloatType(), 0)
        self.run_validator_test(apilib.FloatType(), 0L)
        self.run_validator_test(apilib.FloatType(), None)
        self.run_validator_test(apilib.FloatType(), '123', apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.FloatType(), u'123', apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.FloatType(), '', apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.FloatType(), [], apilib.CommonErrorCodes.INVALID_TYPE)

        self.run_validator_test(apilib.BooleanType(), True)
        self.run_validator_test(apilib.BooleanType(), False)
        self.run_validator_test(apilib.BooleanType(), None)
        self.run_validator_test(apilib.BooleanType(), 0, apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.BooleanType(), '', apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.BooleanType(), [], apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.BooleanType(), {}, apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.BooleanType(), 123, apilib.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(apilib.BooleanType(), u'hello', apilib.CommonErrorCodes.INVALID_TYPE)

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

if __name__ == '__main__':
    unittest.main()
