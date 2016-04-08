import unittest

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

if __name__ == '__main__':
    unittest.main()
