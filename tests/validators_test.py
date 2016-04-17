import decimal
import unittest

import apilib

VC = apilib.ValidationContext

class ValidatorsTest(unittest.TestCase):
    def run_validator_test(self, validator, value, *error_codes):
        self.run_validator_test_for_method(validator, value, None, *error_codes)

    def run_validator_test_for_method(self, validator, value, method, *error_codes):
        return self.run_validator_test_for_context(validator, value,  apilib.ValidationContext(method=method), *error_codes)

    def run_validator_test_for_context(self, validator, value, context, *error_codes):
        error_context = apilib.ErrorContext()
        validator.validate(value, error_context, context)
        errors = error_context.all_errors()
        if error_codes:
            self.assertTrue(errors)
            self.assertEqual(len(error_codes), len(errors))
            for error_code in error_codes:
                self.assertHasErrorCode(error_code, errors)
        else:
            self.assertFalse(errors)
        return errors

    def validate(self, validator, value, error_context):
        validator.validate(value, error_context, None)
        return error_context.all_errors()

    def assertHasErrorCode(self, error_code, errors):
        for error in errors:
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

        ec = apilib.ErrorContext().extend(field='fstring')
        apilib.Required().validate(None, ec, VC())
        self.assertEqual(1, len(ec.all_errors()))
        self.assertEqual('fstring', ec.all_errors()[0].path)

    def test_readonly_validator(self):
        Readonly = apilib.Readonly

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

        ec = apilib.ErrorContext().extend(field='fstring')
        apilib.Readonly().validate('foo', ec, VC())
        self.assertFalse(ec.has_errors())

    def test_nonempty_elements_validator(self):
        NonemptyElements = apilib.NonemptyElements

        self.run_validator_test_for_context(NonemptyElements(), None, None)
        self.run_validator_test_for_context(NonemptyElements(), [], None)
        self.run_validator_test_for_context(NonemptyElements(), ['a'], None)
        self.run_validator_test_for_context(NonemptyElements(), [1, 2, 3], None)
        self.run_validator_test_for_context(NonemptyElements(), [0], None)
        self.run_validator_test_for_context(NonemptyElements(), [False], None)
        self.run_validator_test_for_context(NonemptyElements(), [[None]], None)
        self.run_validator_test_for_context(NonemptyElements(), [{'a': None}], None)

        self.run_validator_test_for_context(NonemptyElements(), [None], None, apilib.CommonErrorCodes.NONEMPTY_ITEM_REQUIRED)
        self.run_validator_test_for_context(NonemptyElements(), [[]], None, apilib.CommonErrorCodes.NONEMPTY_ITEM_REQUIRED)
        self.run_validator_test_for_context(NonemptyElements(), [{}], None, apilib.CommonErrorCodes.NONEMPTY_ITEM_REQUIRED)
        self.run_validator_test_for_context(NonemptyElements(), [1, 2, 3, None], None, apilib.CommonErrorCodes.NONEMPTY_ITEM_REQUIRED)
        self.run_validator_test_for_context(NonemptyElements(), [1, 2, 3, []], None, apilib.CommonErrorCodes.NONEMPTY_ITEM_REQUIRED)
        self.run_validator_test_for_context(NonemptyElements(), [1, 2, 3, {}], None, apilib.CommonErrorCodes.NONEMPTY_ITEM_REQUIRED)

        ec = apilib.ErrorContext().extend(field='lint')
        value = NonemptyElements().validate([1, None], ec, None)
        self.assertIsNone(value)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertEqual('lint[1]', ec.all_errors()[0].path)

        ec = apilib.ErrorContext().extend(field='llist')
        value = NonemptyElements().validate([[1], [2], [3], []], ec, None)
        self.assertIsNone(value)
        self.assertEqual(1, len(ec.all_errors()))
        self.assertEqual('llist[3]', ec.all_errors()[0].path)

    def test_unique_validator(self):
        Unique = apilib.Unique

        self.run_validator_test_for_context(Unique(), None, None)
        self.run_validator_test_for_context(Unique(), [], None)
        self.run_validator_test_for_context(Unique(), ['a'], None)
        self.run_validator_test_for_context(Unique(), [1], None)
        self.run_validator_test_for_context(Unique(), [None], None)
        self.run_validator_test_for_context(Unique(), [False], None)
        self.run_validator_test_for_context(Unique(), [True], None)
        self.run_validator_test_for_context(Unique(), [''], None)
        self.run_validator_test_for_context(Unique(), ['a', 'b'], None)
        self.run_validator_test_for_context(Unique(), ['b', 'a', 'c'], None)
        self.run_validator_test_for_context(Unique(), [3, 2, 1], None)
        self.run_validator_test_for_context(Unique(), [False, True], None)

        errors = self.validate(Unique(), [2, 1, 2], apilib.ErrorContext().extend(field='fint'))
        self.assertEqual(1, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('fint[2]', errors[0].path)

        errors = self.validate(Unique(), [9, 8, 7, 6, 7, 8, 9], apilib.ErrorContext().extend(field='fint'))
        self.assertEqual(3, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('fint[4]', errors[0].path)
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[1].code)
        self.assertEqual('fint[5]', errors[1].path)
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[2].code)
        self.assertEqual('fint[6]', errors[2].path)

        errors = self.validate(Unique(), ['a', 'a', 'b', 'a'], apilib.ErrorContext().extend(field='fstring'))
        self.assertEqual(2, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('fstring[1]', errors[0].path)
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[1].code)
        self.assertEqual('fstring[3]', errors[1].path)

        errors = self.validate(Unique(), ['foo', 'a', '', ''], apilib.ErrorContext().extend(field='fstring'))
        self.assertEqual(1, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('fstring[3]', errors[0].path)

        errors = self.validate(Unique(), ['foo', 'a', None, None], apilib.ErrorContext().extend(field='fstring'))
        self.assertEqual(1, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('fstring[3]', errors[0].path)

        value = Unique().validate([2, 1, 2], apilib.ErrorContext(), None)
        self.assertIsNone(value)

    def test_unique_fields_validator(self):
        UniqueFields = apilib.UniqueFields

        self.run_validator_test_for_context(UniqueFields('id'), None, None)
        self.run_validator_test_for_context(UniqueFields('id'), [], None)
        self.run_validator_test_for_context(UniqueFields('id'), [{}], None)
        self.run_validator_test_for_context(UniqueFields('id'), [{}, {}], None)
        self.run_validator_test_for_context(UniqueFields('id'), [{'id': None}], None)
        self.run_validator_test_for_context(UniqueFields('id'), [{'id': None}, {}], None)
        self.run_validator_test_for_context(UniqueFields('id'), [{'id': 1}, {}], None)
        self.run_validator_test_for_context(UniqueFields('id'), [{'id': 1}, {'id': None}], None)
        self.run_validator_test_for_context(UniqueFields('id'), [{'id': 1}, {'id': 2}], None)
        self.run_validator_test_for_context(UniqueFields('id'), [{'id': 1}, {}, {'id': 3}], None)

        errors = self.validate(UniqueFields('id'), [{'id': 1}, {'id': 1}], apilib.ErrorContext().extend(field='lfoo'))
        self.assertEqual(1, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('lfoo[1].id', errors[0].path)

        errors = self.validate(UniqueFields('id'), [{'id': 1}, {'id': 1}, None, {'id': 1}], apilib.ErrorContext().extend(field='lfoo'))
        self.assertEqual(2, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('lfoo[1].id', errors[0].path)
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[1].code)
        self.assertEqual('lfoo[3].id', errors[1].path)

        errors = self.validate(UniqueFields('id'), [{'id': None}, {'id': None}], apilib.ErrorContext().extend(field='lfoo'))
        self.assertEqual(1, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('lfoo[1].id', errors[0].path)

        errors = self.validate(UniqueFields('foo'), [{'foo': 'a'}, {'foo': 'a'}], apilib.ErrorContext().extend(field='lfoo'))
        self.assertEqual(1, len(errors))
        self.assertEqual(apilib.CommonErrorCodes.DUPLICATE_VALUE, errors[0].code)
        self.assertEqual('lfoo[1].foo', errors[0].path)

        value = UniqueFields('id').validate([{'id': 1}, {'id': 1}],  apilib.ErrorContext(), None)
        self.assertIsNone(value)

    def test_range_validator(self):
        Range = apilib.Range
        VALUE_NOT_IN_RANGE = apilib.CommonErrorCodes.VALUE_NOT_IN_RANGE

        self.run_validator_test_for_context(Range(min_=1), 1, None)
        self.run_validator_test_for_context(Range(min_=1), 2, None)
        self.run_validator_test_for_context(Range(min_=1), 1.1, None)
        self.run_validator_test_for_context(Range(min_=1), 1e6, None)
        self.run_validator_test_for_context(Range(min_=-0.5), -0.1, None)
        self.run_validator_test_for_context(Range(min_=1, max_=3), 1, None)
        self.run_validator_test_for_context(Range(min_=1, max_=3), 2, None)
        self.run_validator_test_for_context(Range(min_=1, max_=3), 2.9, None)
        self.run_validator_test_for_context(Range(min_=1, max_=3), 3, None)
        self.run_validator_test_for_context(Range(max_=3), 1, None)
        self.run_validator_test_for_context(Range(max_=3), 2, None)
        self.run_validator_test_for_context(Range(max_=3), 2.9, None)
        self.run_validator_test_for_context(Range(max_=3), 3, None)
        self.run_validator_test_for_context(Range(max_=-1), -2, None)
        self.run_validator_test_for_context(Range(min_='a'), 'b', None)
        self.run_validator_test_for_context(Range(min_='a', max_='c'), 'b', None)

        self.run_validator_test_for_context(Range(min_=1), 0, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=1), 0.9, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=1), -1, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=1), -1e6, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=-5), -10.5, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=-5), -5.0000001, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=1, max_=3), 0.9, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=1, max_=3), 3.1, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=1, max_=3), -10, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_=1, max_=3), 0, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(max_=3), 3.1, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(max_=3), 4, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(max_=3), 9e5, None, VALUE_NOT_IN_RANGE)
        self.run_validator_test_for_context(Range(min_='a', max_='c'), 'd', None, VALUE_NOT_IN_RANGE)

        ec = apilib.ErrorContext().extend(field='foo')
        value = Range(min_=1).validate(0, ec, None)
        self.assertIsNone(value)

        errors = self.validate(Range(min_=1), 0, apilib.ErrorContext().extend(field='foo'))
        self.assertEqual(1, len(errors))
        self.assertEqual('foo', errors[0].path)
        self.assertEqual('Value 0 is less than 1', errors[0].msg)

        errors = self.validate(Range(max_=10), 15.5, apilib.ErrorContext().extend(field='foo'))
        self.assertEqual(1, len(errors))
        self.assertEqual('foo', errors[0].path)
        self.assertEqual('Value 15.5 is greater than 10', errors[0].msg)

        errors = self.validate(Range(min_=5, max_=10), 4, apilib.ErrorContext().extend(field='foo'))
        self.assertEqual(1, len(errors))
        self.assertEqual('foo', errors[0].path)
        self.assertEqual('Value 4 is less than 5', errors[0].msg)

        errors = self.validate(Range(min_=5, max_=10), 11, apilib.ErrorContext().extend(field='foo'))
        self.assertEqual(1, len(errors))
        self.assertEqual('foo', errors[0].path)
        self.assertEqual('Value 11 is greater than 10', errors[0].msg)


if __name__ == '__main__':
    unittest.main()
