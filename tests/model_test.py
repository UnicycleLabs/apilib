import datetime
import decimal
import unittest

from dateutil import tz

import apilib

class BasicScalarModel(apilib.Model):
    fstring = apilib.Field(apilib.String())
    fint = apilib.Field(apilib.Integer())
    ffloat = apilib.Field(apilib.Float())
    fbool = apilib.Field(apilib.Boolean())

class EmptiesAndUnknownsTest(unittest.TestCase):
    def test_instantiate_empties(self):
        m = BasicScalarModel()
        self.assertIsNone(m.fstring)
        self.assertIsNone(m.fint)
        self.assertIsNone(m.ffloat)
        self.assertIsNone(m.fbool)

    def test_serialize_empties(self):
        obj = BasicScalarModel().to_json()
        self.assertEqual({}, obj)

    def test_deserialize_empties(self):
        m = BasicScalarModel.from_json({})
        self.assertIsNone(m.fstring)
        self.assertIsNone(m.fint)
        self.assertIsNone(m.ffloat)
        self.assertIsNone(m.fbool)

    def test_instantiate_unknown_field(self):
        with self.assertRaises(apilib.UnknownFieldException) as e:
            BasicScalarModel(fint=1, foo=2)
        self.assertEqual('Unknown field "foo"', e.exception.message)

    def test_deserialize_unknown_field(self):
        m = BasicScalarModel.from_json({'foo': 'blah'})
        self.assertIsNotNone(m)
        self.assertFalse(hasattr(m, 'foo'))

class BasicScalerFieldsTest(unittest.TestCase):
    def test_instantiate(self):
        m = BasicScalarModel(fstring='a string', fint=120, ffloat=2.57, fbool=True)
        self.assertEqual('a string', m.fstring)
        self.assertEqual(120, m.fint)
        self.assertEqual(2.57, m.ffloat)
        self.assertEqual(True, m.fbool)

    def test_serialize(self):
        m = BasicScalarModel(fstring='a string', fint=120, ffloat=2.57, fbool=True)
        self.assertEqual({'ffloat': 2.57, 'fint': 120, 'fstring': u'a string', 'fbool': True}, m.to_json())

    def test_deserialize(self):
        m = BasicScalarModel.from_json({'ffloat': 2.57, 'fint': 120, 'fstring': u'a string', 'fbool': True})
        self.assertEqual('a string', m.fstring)
        self.assertEqual(120, m.fint)
        self.assertEqual(2.57, m.ffloat)
        self.assertEqual(True, m.fbool)

    def test_deserialization_type_casting(self):
        m = BasicScalarModel.from_json({'ffloat': '2.57', 'fint': '120', 'fstring': 1234, 'fbool': '1'})
        self.assertEqual('1234', m.fstring)
        self.assertEqual(120, m.fint)
        self.assertEqual(2.57, m.ffloat)
        self.assertEqual(True, m.fbool)


class ScalarListModel(apilib.Model):
    lstring = apilib.ListField(apilib.String())
    lint = apilib.ListField(apilib.Integer())
    lfloat = apilib.ListField(apilib.Float())
    lbool = apilib.ListField(apilib.Boolean())

class ScalarListsTest(unittest.TestCase):
    def test_instantiate_empties(self):
        m = ScalarListModel()
        self.assertIsNone(m.lstring)
        self.assertIsNone(m.lint)
        self.assertIsNone(m.lfloat)
        self.assertIsNone(m.lbool)

    def test_serialize_empties(self):
        self.assertEqual({}, ScalarListModel().to_json())

    def test_deserialize_empties(self):
        m = ScalarListModel.from_json({})
        self.assertIsNone(m.lstring)
        self.assertIsNone(m.lint)
        self.assertIsNone(m.lfloat)
        self.assertIsNone(m.lbool)

        m = ScalarListModel.from_json({'lstring': None, 'lint': None, 'lfloat': None, 'lbool': None})
        self.assertIsNone(m.lstring)
        self.assertIsNone(m.lint)
        self.assertIsNone(m.lfloat)
        self.assertIsNone(m.lbool)

        m = ScalarListModel.from_json({'lstring': [], 'lint': [], 'lfloat': [], 'lbool': []})
        self.assertEqual([], m.lstring)
        self.assertEqual([], m.lint)
        self.assertEqual([], m.lfloat)
        self.assertEqual([], m.lbool)

    def test_instantiate(self):
        m = ScalarListModel(lstring=['a', 'b', 'c'], lint=[5], lfloat=(2.0, 3.5), lbool=[False, True, False])
        self.assertEqual(['a', 'b', 'c'], m.lstring)
        self.assertEqual([5], m.lint)
        self.assertEqual([2.0, 3.5], m.lfloat)
        self.assertEqual([False, True, False], m.lbool)

        m = ScalarListModel(lstring=['a', 'b', None], lint=[None], lfloat=(2.0, None), lbool=[None, None, False])
        self.assertEqual(['a', 'b', None], m.lstring)
        self.assertEqual([None], m.lint)
        self.assertEqual([2.0, None], m.lfloat)
        self.assertEqual([None, None, False], m.lbool)

    def test_serialize(self):
        m = ScalarListModel(lstring=['a', 'b', 'c'], lint=[5], lfloat=(2.0, 3.5), lbool=[False, True, False])
        self.assertEqual(
            {'lstring': [u'a', u'b', u'c'], 'lbool': [False, True, False], 'lint': [5], 'lfloat': [2.0, 3.5]},
            m.to_json())

        m = ScalarListModel(lstring=['a', 'b', None], lint=[None], lfloat=(2.0, None), lbool=[None, None, False])
        self.assertEqual(
            {'lstring': [u'a', u'b', None], 'lbool': [None, None, False], 'lint': [None], 'lfloat': [2.0, None]},
            m.to_json())

        m = ScalarListModel(lint=[None])
        self.assertEqual({'lint': [None]}, m.to_json())

    def test_deserialize(self):
        m = ScalarListModel.from_json({'lstring': [u'a', u'b', u'c'], 'lbool': [False, True, False], 'lint': [5], 'lfloat': [2.0, 3.5]})
        self.assertEqual(['a', 'b', 'c'], m.lstring)
        self.assertEqual([5], m.lint)
        self.assertEqual([2.0, 3.5], m.lfloat)
        self.assertEqual([False, True, False], m.lbool)

        m = ScalarListModel.from_json({'lstring': [u'a', u'b', None], 'lbool': [None, None, False], 'lint': [None], 'lfloat': [2.0, None]})
        self.assertEqual(['a', 'b', None], m.lstring)
        self.assertEqual([None], m.lint)
        self.assertEqual([2.0, None], m.lfloat)
        self.assertEqual([None, None, False], m.lbool)

        m = ScalarListModel.from_json({'lint': [None]})
        self.assertIsNone(m.lstring)
        self.assertEqual([None], m.lint)
        self.assertIsNone(m.lfloat)
        self.assertIsNone(m.lbool)

    def test_deserialization_type_casting(self):
        m = ScalarListModel.from_json({'lstring': [1, u'b', 3], 'lbool': ['a', True, False], 'lint': ['5', 6.0], 'lfloat': ['2.0', '-1']})
        self.assertEqual(['1', 'b', '3'], m.lstring)
        self.assertEqual([5, 6], m.lint)
        self.assertEqual([2.0, -1.0], m.lfloat)
        self.assertEqual([True, True, False], m.lbool)


class BasicChildModel(apilib.Model):
    fstring = apilib.Field(apilib.String())

class BasicParentModel(apilib.Model):
    fchild = apilib.ModelField(BasicChildModel)
    lchild = apilib.ListField(BasicChildModel)

class BasicNestedModelTest(unittest.TestCase):
    def test_empties(self):
        m = BasicParentModel()
        self.assertIsNone(m.fchild)
        self.assertIsNone(m.lchild)

        m = BasicParentModel(fchild=None, lchild=None)
        self.assertIsNone(m.fchild)
        self.assertIsNone(m.lchild)

        m = BasicParentModel(lchild=[])
        self.assertEqual([], m.lchild)

        m = BasicParentModel(lchild=[None, None])
        self.assertEqual([None, None], m.lchild)

        m = BasicParentModel()
        self.assertEqual({}, m.to_json())

        m = BasicParentModel(fchild=None, lchild=None)
        self.assertEqual({'lchild': None, 'fchild': None}, m.to_json())

        m = BasicParentModel(lchild=[])
        self.assertEqual({'lchild': []}, m.to_json())

        m = BasicParentModel.from_json({})
        self.assertIsNone(m.fchild)
        self.assertIsNone(m.lchild)

        m = BasicParentModel.from_json({'lchild': [], 'fchild': None})
        self.assertIsNone(m.fchild)
        self.assertEqual([], m.lchild)

        m = BasicParentModel.from_json({'lchild': None, 'fchild': None})
        self.assertIsNone(m.fchild)
        self.assertIsNone(m.lchild)

        m = BasicParentModel.from_json({'fchild': {}})
        self.assertIsNotNone(m.fchild)
        self.assertIsNone(m.fchild.fstring)

        m = BasicParentModel.from_json({'lchild': [None, {}]})
        self.assertIsNotNone(m.lchild)
        self.assertEqual(2, len(m.lchild))
        self.assertIsNone(m.lchild[0])
        self.assertIsNotNone(m.lchild[1])
        self.assertIsNone(m.lchild[1].fstring)

    def test_instantiate(self):
        m = BasicParentModel(
            fchild=BasicChildModel(fstring='a'),
            lchild=[BasicChildModel(fstring='b'), BasicChildModel(fstring='c')])
        self.assertIsNotNone(m.fchild)
        self.assertEqual('a', m.fchild.fstring)
        self.assertIsNotNone(m.lchild)
        self.assertEqual(2, len(m.lchild))
        self.assertEqual('b', m.lchild[0].fstring)
        self.assertEqual('c', m.lchild[1].fstring)

    def test_serialize(self):
        m = BasicParentModel(
            fchild=BasicChildModel(fstring='a'),
            lchild=[BasicChildModel(fstring='b'), BasicChildModel(fstring='c')])
        self.assertEqual(
            {'lchild': [{'fstring': u'b'}, {'fstring': u'c'}], 'fchild': {'fstring': u'a'}},
            m.to_json())

    def test_deserialize(self):
        m = BasicParentModel.from_json({'lchild': [{'fstring': u'b'}, {'fstring': u'c'}], 'fchild': {'fstring': u'a'}})
        self.assertIsNotNone(m.fchild)
        self.assertEqual('a', m.fchild.fstring)
        self.assertIsNotNone(m.lchild)
        self.assertEqual(2, len(m.lchild))
        self.assertEqual('b', m.lchild[0].fstring)
        self.assertEqual('c', m.lchild[1].fstring)

class ModelWithDates(apilib.Model):
    fdate = apilib.Field(apilib.Date())
    fdatetime = apilib.Field(apilib.DateTime())

class ModelWithDateList(apilib.Model):
    ldate = apilib.ListField(apilib.Date())
    ldatetime = apilib.ListField(apilib.DateTime())

class DateFieldTest(unittest.TestCase):
    def test_empties(self):
        m = ModelWithDates()
        self.assertIsNone(m.fdate)
        self.assertIsNone(m.fdatetime)

        m = ModelWithDates(fdate=None, fdatetime=None)
        self.assertIsNone(m.fdate)
        self.assertIsNone(m.fdatetime)

        m = ModelWithDates()
        self.assertEqual({}, m.to_json())

        m = ModelWithDates(fdate=None, fdatetime=None)
        self.assertEqual({'fdate': None, 'fdatetime': None}, m.to_json())

        m = ModelWithDates.from_json({})
        self.assertIsNone(m.fdate)
        self.assertIsNone(m.fdatetime)

        m = ModelWithDates.from_json({'fdate': None, 'fdatetime': None})
        self.assertIsNone(m.fdate)
        self.assertIsNone(m.fdatetime)

    def test_instantiate(self):
        m = ModelWithDates(
            fdate=datetime.date(2016, 2, 18),
            fdatetime=datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.tzutc()))
        self.assertEqual(datetime.date(2016, 2, 18), m.fdate)
        self.assertEqual(datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.tzutc()), m.fdatetime)

        m = ModelWithDates(
            fdate=datetime.date(2034, 5, 10),
            fdatetime=datetime.datetime(2050, 8, 18))
        self.assertEqual(datetime.date(2034, 5, 10), m.fdate)
        self.assertEqual(datetime.datetime(2050, 8, 18), m.fdatetime)

        m = ModelWithDates(
            fdate=datetime.date(2016, 2, 18),
            fdatetime=datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.gettz('America/Los_Angeles')))
        self.assertEqual(datetime.date(2016, 2, 18), m.fdate)
        self.assertEqual(datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.gettz('America/Los_Angeles')), m.fdatetime)

    def test_serialize(self):
        m = ModelWithDates(
            fdate=datetime.date(2016, 2, 18),
            fdatetime=datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.tzutc()))
        self.assertEqual(
            {'fdatetime': u'2012-04-12T10:08:23+00:00', 'fdate': u'2016-02-18'},
            m.to_json())

        m = ModelWithDates(
            fdate=datetime.date(2034, 5, 10),
            fdatetime=datetime.datetime(2050, 8, 18))
        self.assertEqual(
            {'fdatetime': u'2050-08-18T00:00:00', 'fdate': u'2034-05-10'},
            m.to_json())

        m = ModelWithDates(
            fdate=datetime.date(2016, 2, 18),
            fdatetime=datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.gettz('America/Los_Angeles')))
        self.assertEqual(
            {'fdatetime': u'2012-04-12T10:08:23-07:00', 'fdate': u'2016-02-18'},
            m.to_json())

    def test_deserialize(self):
        m = ModelWithDates.from_json({'fdatetime': u'2012-04-12T10:08:23+00:00', 'fdate': u'2016-02-18'})
        self.assertEqual(datetime.date(2016, 2, 18), m.fdate)
        self.assertEqual(datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.tzutc()), m.fdatetime)

        m = ModelWithDates.from_json({'fdatetime': u'2050-08-18T00:00:00', 'fdate': u'2034-05-10'})
        self.assertEqual(datetime.date(2034, 5, 10), m.fdate)
        self.assertEqual(datetime.datetime(2050, 8, 18), m.fdatetime)

        m = ModelWithDates.from_json({'fdatetime': u'2012-04-12T10:08:23-07:00', 'fdate': u'2016-02-18'})
        self.assertEqual(datetime.date(2016, 2, 18), m.fdate)
        self.assertEqual(datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.gettz('America/Los_Angeles')), m.fdatetime)

    def test_serialize_lists(self):
        m = ModelWithDateList(
            ldate=[datetime.date(2016, 3, 10), datetime.date(2016, 4, 15)],
            ldatetime=[datetime.datetime(2010, 1, 12, 10, 8, 23, tzinfo=tz.gettz('America/Los_Angeles')),
                datetime.datetime(2013, 2, 12, 14, 29, 0, tzinfo=tz.gettz('America/New_York'))])
        self.assertEqual(
            {'ldatetime': [u'2010-01-12T10:08:23-08:00', u'2013-02-12T14:29:00-05:00'], 'ldate': [u'2016-03-10', u'2016-04-15']},
            m.to_json())

    def test_deserialize_lists(self):
        m = ModelWithDateList.from_json({
            'ldatetime': [u'2010-01-12T10:08:23-08:00', u'2013-02-12T14:29:00-05:00'],
            'ldate': [u'2016-03-10', u'2016-04-15'],
            })
        self.assertEqual([datetime.date(2016, 3, 10), datetime.date(2016, 4, 15)], m.ldate)
        self.assertEqual(
            [datetime.datetime(2010, 1, 12, 10, 8, 23, tzinfo=tz.gettz('America/Los_Angeles')),
                datetime.datetime(2013, 2, 12, 14, 29, 0, tzinfo=tz.gettz('America/New_York'))],
            m.ldatetime)

class ModelWithExtendedFields(apilib.Model):
    ldecimal = apilib.Field(apilib.Decimal())
    lenum = apilib.Field(apilib.Enum(['Jerry', 'George']))

class ExtendedFieldsTest(unittest.TestCase):
    def test_empties(self):
        m = ModelWithExtendedFields()
        self.assertIsNone(m.ldecimal)
        self.assertIsNone(m.lenum)

        m = ModelWithExtendedFields(ldecimal=None, lenum=None)
        self.assertIsNone(m.ldecimal)
        self.assertIsNone(m.lenum)

        m = ModelWithExtendedFields()
        self.assertEqual({}, m.to_json())

        m = ModelWithExtendedFields(ldecimal=None, lenum=None)
        self.assertEqual({'ldecimal': None, 'lenum': None}, m.to_json())

        m = ModelWithExtendedFields.from_json({})
        self.assertIsNone(m.ldecimal)
        self.assertIsNone(m.lenum)

        m = ModelWithExtendedFields.from_json({'ldecimal': None, 'lenum': None})
        self.assertIsNone(m.ldecimal)
        self.assertIsNone(m.lenum)

    def test_serialize(self):
        m = ModelWithExtendedFields(ldecimal=decimal.Decimal('0.1'), lenum='Jerry')
        self.assertEqual({'ldecimal': u'0.1', 'lenum': u'Jerry'}, m.to_json())

    def test_deserialize(self):
        m = ModelWithExtendedFields.from_json({'ldecimal': u'0.1', 'lenum': u'Jerry'})
        self.assertEqual(decimal.Decimal, type(m.ldecimal))
        self.assertEqual(decimal.Decimal('0.1'), m.ldecimal)
        self.assertEqual('Jerry', m.lenum)

class NGrandchild(apilib.Model):
    fint = apilib.Field(apilib.Integer())
    lfloat = apilib.ListField(apilib.Float())

class NChild(apilib.Model):
    fgrandchild = apilib.ModelField(NGrandchild)
    lgrandchild = apilib.ListField(NGrandchild)
    fstring = apilib.Field(apilib.String())

class NParent(apilib.Model):
    fchild = apilib.ModelField(NChild)
    lchild = apilib.ListField(NChild)

class MultipleNestingTest(unittest.TestCase):
    def test_serialize(self):
        m = NParent(
            fchild=NChild(
                fgrandchild=NGrandchild(fint=1, lfloat=[2.0, 3.0]),
                lgrandchild=[NGrandchild(fint=4, lfloat=[5.0])],
                fstring='abc'),
            lchild=[NChild(
                fgrandchild=NGrandchild(fint=6, lfloat=[7.0]),
                lgrandchild=[NGrandchild(fint=8, lfloat=[9.0])],
                fstring='def')])
        self.assertDictEqual(
            {'fchild': {'fgrandchild': {'fint': 1, 'lfloat': [2.0, 3.0]},
                        'fstring': u'abc',
                        'lgrandchild': [{'fint': 4, 'lfloat': [5.0]}]},
             'lchild': [{'fgrandchild': {'fint': 6, 'lfloat': [7.0]},
                         'fstring': u'def',
                         'lgrandchild': [{'fint': 8, 'lfloat': [9.0]}]}]},
            m.to_json())

    def test_deserialize(self):
        m = NParent.from_json(
             {'fchild': {'fgrandchild': {'fint': 1, 'lfloat': [2.0, 3.0]},
                        'fstring': u'abc',
                        'lgrandchild': [{'fint': 4, 'lfloat': [5.0]}]},
             'lchild': [{'fgrandchild': {'fint': 6, 'lfloat': [7.0]},
                         'fstring': u'def',
                         'lgrandchild': [{'fint': 8, 'lfloat': [9.0]}]}]})
        self.assertIsNotNone(m.fchild)
        self.assertIsNotNone(m.lchild)

        self.assertEqual(1, m.fchild.fgrandchild.fint)
        self.assertEqual([2.0, 3.0], m.fchild.fgrandchild.lfloat)
        self.assertEqual(1, len(m.fchild.lgrandchild))
        self.assertEqual(4, m.fchild.lgrandchild[0].fint)
        self.assertEqual([5.0], m.fchild.lgrandchild[0].lfloat)
        self.assertEqual('abc', m.fchild.fstring)

        self.assertEqual(1, len(m.lchild))
        self.assertEqual(6, m.lchild[0].fgrandchild.fint)
        self.assertEqual([7.0], m.lchild[0].fgrandchild.lfloat)
        self.assertEqual(1, len(m.lchild[0].lgrandchild))
        self.assertEqual(8, m.lchild[0].lgrandchild[0].fint)
        self.assertEqual([9.0], m.lchild[0].lgrandchild[0].lfloat)
        self.assertEqual('def', m.lchild[0].fstring)

class ToStringModel(apilib.Model):
    fstring = apilib.Field(apilib.String())
    fint = apilib.Field(apilib.Integer())
    ffloat = apilib.Field(apilib.Float())
    fbool = apilib.Field(apilib.Boolean())
    fdate = apilib.Field(apilib.Date())
    fdatetime = apilib.Field(apilib.DateTime())
    fdecimal = apilib.Field(apilib.Decimal())
    fenum = apilib.Field(apilib.Enum(['JERRY', 'GEORGE']))
    fchild = apilib.ModelField(BasicScalarModel)
    lchild = apilib.ListField(BasicScalarModel)

class ToStringTest(unittest.TestCase):
    def test_foo(self):
        m = ToStringModel(
            fstring='hello\'world',
            fint=123,
            ffloat=0.1,
            fbool=False,
            fdate=datetime.date(2016, 2, 18),
            fdatetime=datetime.datetime(2012, 4, 12, 10, 8, 23, tzinfo=tz.tzutc()),
            fdecimal=decimal.Decimal('0.1'),
            fenum='JERRY',
            fchild=BasicScalarModel(
                fstring=None,
                ffloat=None),
            lchild=[
                BasicScalarModel(
                    fstring='345',
                    fint=-543,
                    ffloat=-0.0002,
                    fbool=True),
                BasicScalarModel(
                    fbool=None),
                BasicScalarModel(),
            ])
        expected = '''
<ToStringModel: {
  fbool: False,
  fchild: <BasicScalarModel: {
    ffloat: None,
    fstring: None,
  }>,
  fdate: 2016-02-18,
  fdatetime: 2012-04-12 10:08:23+00:00,
  fdecimal: 0.1,
  fenum: JERRY,
  ffloat: 0.1,
  fint: 123,
  fstring: 'hello\\'world',
  lchild: [
  <BasicScalarModel: {
      fbool: True,
      ffloat: -0.0002,
      fint: -543,
      fstring: '345',
    }>
  <BasicScalarModel: {
      fbool: None,
    }>
  <BasicScalarModel: {
    }>
  ],
}>'''[1:]
        self.assertEqual(expected, str(m))

if __name__ == '__main__':
    unittest.main()
