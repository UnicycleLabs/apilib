import unittest

import apilib

class FooRequest(apilib.Request):
    request_str = apilib.Field(apilib.String(), required=True)

class FooResponse(apilib.Response):
    response_str = apilib.Field(apilib.String())

class FooService(apilib.Service):
    methods = apilib.servicemethods(
        apilib.Meth('foo', FooRequest, FooResponse),
        apilib.Meth('unimplemented', None, None))

class FooServiceImpl(FooService, apilib.ServiceImplementation):
    def foo(self, request):
        return FooResponse(response_str='Your request string was: %s' % request.request_str)

class BasicServiceTest(unittest.TestCase):
    def test_unknown_method(self):
        service = FooServiceImpl()
        with self.assertRaises(apilib.exceptions.MethodNotFoundException) as context:
            service.invoke_with_json('unknown', {})
        e = context.exception
        self.assertEqual('No descriptor for method of name "unknown"', e.message)

    def test_unimplemented_method(self):
        service = FooServiceImpl()
        with self.assertRaises(apilib.exceptions.MethodNotImplementedException) as context:
            service.invoke_with_json('unimplemented', {})
        e = context.exception
        self.assertEqual('Method "unimplemented" not implemented', e.message)

    def test_validation(self):
        service = FooServiceImpl()
        with self.assertRaises(apilib.ApiException) as context:
            service.invoke_with_json('foo', {'request_str': None})
        e = context.exception
        self.assertEqual(1, len(e.errors))
        self.assertEqual(apilib.CommonErrorCodes.REQUIRED, e.errors[0].code)
        self.assertEqual('request_str', e.errors[0].path)
        self.assertEqual('Field is required', e.errors[0].message)

    def test_successful_response(self):
        service = FooServiceImpl()
        response = service.invoke_with_json('foo', {'request_str': 'blah'})
        self.assertIsNotNone(response)
        self.assertEqual({'response_str': u'Your request string was: blah', 'response_code': u'SUCCESS'}, response)


if __name__ == '__main__':
    unittest.main()
