import datetime
import decimal
import unittest

from dateutil import tz

import apilib

apilib.model.ID_ENCRYPTION_KEY = 'test'

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
        with self.assertRaises(apilib.DeserializationError) as e:
            BasicScalarModel.from_json({'foo': 'blah'})
        self.assertEqual(1, len(e.exception.errors))
        self.assertEqual(apilib.CommonErrorCodes.UNKNOWN_FIELD, e.exception.errors[0].code)
        self.assertEqual('foo', e.exception.errors[0].path)

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


class ScalarListModel(apilib.Model):
    lstring = apilib.Field(apilib.ListType(apilib.String()))
    lint = apilib.Field(apilib.ListType(apilib.Integer()))
    lfloat = apilib.Field(apilib.ListType(apilib.Float()))
    lbool = apilib.Field(apilib.ListType(apilib.Boolean()))

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


class BasicChildModel(apilib.Model):
    fstring = apilib.Field(apilib.String())

class BasicParentModel(apilib.Model):
    fchild = apilib.Field(apilib.ModelType(BasicChildModel))
    lchild = apilib.Field(apilib.ListType(BasicChildModel))

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
    ldate = apilib.Field(apilib.ListType(apilib.Date()))
    ldatetime = apilib.Field(apilib.ListType(apilib.DateTime()))

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
    fdecimal = apilib.Field(apilib.Decimal())
    fenum = apilib.Field(apilib.Enum(['Jerry', 'George']))
    fid = apilib.Field(apilib.EncryptedId())

class ExtendedFieldsTest(unittest.TestCase):
    def test_empties(self):
        m = ModelWithExtendedFields()
        self.assertIsNone(m.fdecimal)
        self.assertIsNone(m.fenum)

        m = ModelWithExtendedFields(fdecimal=None, fenum=None, fid=None)
        self.assertIsNone(m.fdecimal)
        self.assertIsNone(m.fenum)
        self.assertIsNone(m.fid)

        m = ModelWithExtendedFields()
        self.assertEqual({}, m.to_json())

        m = ModelWithExtendedFields(fdecimal=None, fenum=None, fid=None)
        self.assertEqual({'fdecimal': None, 'fenum': None, 'fid': None}, m.to_json())

        m = ModelWithExtendedFields.from_json({})
        self.assertIsNone(m.fdecimal)
        self.assertIsNone(m.fenum)
        self.assertIsNone(m.fid)

        m = ModelWithExtendedFields.from_json({'fdecimal': None, 'fenum': None, 'fid': None})
        self.assertIsNone(m.fdecimal)
        self.assertIsNone(m.fenum)
        self.assertIsNone(m.fid)

    def test_serialize(self):
        m = ModelWithExtendedFields(fdecimal=decimal.Decimal('0.1'), fenum='Jerry', fid=123)
        self.assertEqual({'fdecimal': u'0.1', 'fenum': u'Jerry', 'fid': 'PYW33gW8'}, m.to_json())

    def test_deserialize(self):
        m = ModelWithExtendedFields.from_json({'fdecimal': u'0.1', 'fenum': u'Jerry', 'fid': 'PYW33gW8'})
        self.assertEqual(decimal.Decimal, type(m.fdecimal))
        self.assertEqual(decimal.Decimal('0.1'), m.fdecimal)
        self.assertEqual('Jerry', m.fenum)
        self.assertEqual(123, m.fid)

class NGrandchild(apilib.Model):
    fint = apilib.Field(apilib.Integer())
    lfloat = apilib.Field(apilib.ListType(apilib.Float()))

class NChild(apilib.Model):
    fgrandchild = apilib.Field(apilib.ModelType(NGrandchild))
    lgrandchild = apilib.Field(apilib.ListType(NGrandchild))
    fstring = apilib.Field(apilib.String())

class NParent(apilib.Model):
    fchild = apilib.Field(apilib.ModelType(NChild))
    lchild = apilib.Field(apilib.ListType(NChild))

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
    fchild = apilib.Field(apilib.ModelType(BasicScalarModel))
    lchild = apilib.Field(apilib.ListType(BasicScalarModel))

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
      }>,
    <BasicScalarModel: {
        fbool: None,
      }>,
    <BasicScalarModel: {
      }>,
    ],
}>'''[1:]
        self.assertEqual(expected, str(m))


class InheritanceFieldMappingTest(unittest.TestCase):
    class Base(apilib.Model):
        base = apilib.Field(apilib.String())

    class Subclass(Base):
        subclass = apilib.Field(apilib.String())

    def test_inheritance_field_mapping(self):
        sm = self.Subclass(base='base string 2', subclass='subclass string 2')
        bm = self.Base(base='base string')
        self.assertIsNotNone(bm)
        self.assertIsNotNone(sm)
        self.assertEqual('base string', bm.base)
        self.assertEqual('base string 2', sm.base)
        self.assertEqual('subclass string 2', sm.subclass)
        self.assertTrue('base' in self.Base._field_name_to_field)
        self.assertFalse('subclass' in self.Base._field_name_to_field)
        self.assertTrue('base' in self.Subclass._field_name_to_field)
        self.assertTrue('subclass' in self.Subclass._field_name_to_field)

if __name__ == '__main__':
    unittest.main()
