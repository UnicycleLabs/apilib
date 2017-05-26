import unittest

import apilib

class ScalarModel(apilib.Model):
    fint = apilib.Field(apilib.Integer())
    fstring = apilib.Field(apilib.String())

class PublicRequest(apilib.Request):
    fcomplex = apilib.Field(apilib.ListType(apilib.ListType(apilib.ModelType(ScalarModel))))

class PublicResponse(apilib.Response):
    response_string = apilib.Field(apilib.String())

class PrivateRequest(apilib.Request):
    private_request_string = apilib.Field(apilib.String())

class PrivateResponse(apilib.Response):
    private_request_string = apilib.Field(apilib.String())


class FooService(apilib.Service):
    path = '/foo_service'
    public = True
    methods = apilib.servicemethods(
        apilib.Meth('public_method', PublicRequest, PublicResponse, public=True),
        apilib.Meth('private_method', PrivateRequest, PrivateResponse, public=False))

class MetaTest(unittest.TestCase):
    def test_get_model_classes(self):
        model_classes = apilib.get_model_classes_from_services([FooService])
        self.assertEqual(6, len(model_classes))
        self.assertIn(ScalarModel, model_classes)
        self.assertIn(PublicRequest, model_classes)
        self.assertIn(PublicResponse, model_classes)
        self.assertIn(PrivateRequest, model_classes)
        self.assertIn(PrivateResponse, model_classes)
        self.assertIn(apilib.ApiError, model_classes)

    def test_get_public_only_model_classes(self):
        model_classes = apilib.get_model_classes_from_services([FooService], public_only=True)
        self.assertEqual(4, len(model_classes))
        self.assertIn(ScalarModel, model_classes)
        self.assertIn(PublicRequest, model_classes)
        self.assertIn(PublicResponse, model_classes)
        self.assertIn(apilib.ApiError, model_classes)

        self.assertNotIn(PrivateRequest, model_classes)
        self.assertNotIn(PrivateResponse, model_classes)

if __name__ == '__main__':
    unittest.main()
