import json
import StringIO
import unittest

import mock
import requests

import apilib

class FooRequest(apilib.Request):
    request_str = apilib.Field(apilib.String(), required=True)

class FooResponse(apilib.Response):
    response_str = apilib.Field(apilib.String())

class FooService(apilib.Service):
    methods = apilib.servicemethods(
        apilib.Meth('foo', FooRequest, FooResponse),
        apilib.Meth('unimplemented', None, None))
    path = '/foo_service'

class FooServiceImpl(FooService, apilib.ServiceImplementation):
    def foo(self, request):
        return FooResponse(response_str='Your request string was: %s' % request.request_str)

class RemoteFooService(FooService, apilib.RemoteServiceStub):
    pass

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
        response = service.invoke_with_json('foo', {'request_str': None})
        self.assertEqual('REQUEST_ERROR', response['response_code'])
        self.assertEqual(1, len(response['errors']))
        self.assertEqual(apilib.CommonErrorCodes.REQUIRED, response['errors'][0]['code'])
        self.assertEqual('request_str', response['errors'][0]['path'])
        self.assertEqual('Field is required', response['errors'][0]['message'])

    def test_successful_response(self):
        service = FooServiceImpl()
        response = service.invoke_with_json('foo', {'request_str': 'blah'})
        self.assertIsNotNone(response)
        self.assertEqual({'response_str': u'Your request string was: blah', 'response_code': u'SUCCESS'}, response)

def mock_requests_json_response(obj):
        response = requests.Response()
        response.raw = StringIO.StringIO(json.dumps(obj))
        response.headers = requests.structures.CaseInsensitiveDict({'Content-Type': 'application/json'})
        return response

class RemoteServiceTest(unittest.TestCase):
    @mock.patch('requests.post')
    def test_remote_request(self, mock_post):
        service = RemoteFooService('http://localhost:5000')
        mock_post.return_value = mock_requests_json_response({'response_str': 'this is a response', 'response_code': 'SUCCESS'})
        foo_response = service.foo(FooRequest(request_str='blah'))
        self.assertIsNotNone(foo_response)
        self.assertEqual('SUCCESS', foo_response.response_code)
        self.assertEqual('this is a response', foo_response.response_str)
        self.assertIsNone(foo_response.errors)
        self.assertEqual(1, mock_post.call_count)
        self.assertEqual('http://localhost:5000/foo_service/foo', mock_post.call_args[0][0])
        self.assertEqual('{"request_str": "blah"}', mock_post.call_args[1]['data'])
        self.assertEqual({'Content-Type': 'application/json'}, mock_post.call_args[1]['headers'])

    @mock.patch('requests.post')
    def test_trailing_slashes_removed_from_urls(self, mock_post):
        class AltRemoteFooService(RemoteFooService):
            path = '/foo_service/'
        service = AltRemoteFooService('http://localhost:5000/')
        mock_post.return_value = mock_requests_json_response({'response_str': 'this is a response', 'response_code': 'SUCCESS'})
        foo_response = service.foo(FooRequest(request_str='blah'))
        self.assertIsNotNone(foo_response)
        self.assertEqual('SUCCESS', foo_response.response_code)
        self.assertEqual('this is a response', foo_response.response_str)
        self.assertIsNone(foo_response.errors)
        self.assertEqual(1, mock_post.call_count)
        self.assertEqual('http://localhost:5000/foo_service/foo', mock_post.call_args[0][0])
        self.assertEqual('{"request_str": "blah"}', mock_post.call_args[1]['data'])
        self.assertEqual({'Content-Type': 'application/json'}, mock_post.call_args[1]['headers'])

    def test_unknown_method(self):
        service = RemoteFooService('http://localhost:5000')
        with self.assertRaises(apilib.MethodNotFoundException) as context:
            service.unknown(FooRequest(request_str='blah'))
        self.assertEqual('No method named "unknown" defined on this service', context.exception.message)

class Widget(apilib.Model):
    id = apilib.Field(apilib.String(), required=['delete', 'mutate/UPDATE', 'NonwidgetService.get'])

class WidgetOperation(apilib.Operation):
    operand = apilib.Field(apilib.ModelType(Widget), required=True)

class WidgetRequest(apilib.Request):
    operations = apilib.Field(apilib.ListType(WidgetOperation))

class WidgetResponse(apilib.Response):
    pass

class WidgetService(apilib.Service):
    methods = apilib.servicemethods(
        apilib.Meth('get', WidgetRequest, WidgetResponse),
        apilib.Meth('mutate', WidgetRequest, WidgetResponse),
        apilib.Meth('delete', WidgetRequest, WidgetResponse))

class WidgetServiceImpl(WidgetService, apilib.ServiceImplementation):
    def get(self, request):
        return WidgetResponse()
    def mutate(self, request):
        return WidgetResponse()
    def delete(self, request):
        return WidgetResponse()

class NonwidgetService(WidgetService):
    pass

class NonwidgetServiceImpl(NonwidgetService, apilib.ServiceImplementation):
    def get(self, request):
        return WidgetResponse()
    def mutate(self, request):
        return WidgetResponse()
    def delete(self, request):
        return WidgetResponse()

class ServiceValidationTest(unittest.TestCase):
    def test_field_required_only_on_specific_methods_and_services(self):
        widget_service = WidgetServiceImpl()
        no_id_add_request = {'operations': [{'operator': 'ADD', 'operand': {'id': None}}]}
        response = widget_service.invoke_with_json('delete', no_id_add_request)
        self.assertEqual('REQUEST_ERROR', response['response_code'])
        self.assertEqual(1, len(response['errors']))
        self.assertEqual(apilib.CommonErrorCodes.REQUIRED, response['errors'][0]['code'])
        self.assertEqual('operations[0].operand.id', response['errors'][0]['path'])
        self.assertEqual('Field is required on method(s) "delete, mutate/UPDATE, NonwidgetService.get"', response['errors'][0]['message'])

        response = widget_service.invoke_with_json('mutate', no_id_add_request)
        self.assertIsNotNone(response)
        self.assertEqual('SUCCESS', response.get('response_code'))

        no_id_set_request = {'operations': [{'operator': 'UPDATE', 'operand': {'id': None}}]}
        response = widget_service.invoke_with_json('mutate', no_id_set_request)
        self.assertEqual('REQUEST_ERROR', response['response_code'])
        self.assertEqual(1, len(response['errors']))
        self.assertEqual(apilib.CommonErrorCodes.REQUIRED, response['errors'][0]['code'])
        self.assertEqual('operations[0].operand.id', response['errors'][0]['path'])
        self.assertEqual('Field is required on method(s) "delete, mutate/UPDATE, NonwidgetService.get"', response['errors'][0]['message'])

        response = widget_service.invoke_with_json('get', no_id_add_request)
        self.assertIsNotNone(response)
        self.assertEqual('SUCCESS', response.get('response_code'))

        nonwidget_service = NonwidgetServiceImpl()
        response = nonwidget_service.invoke_with_json('get', no_id_add_request)
        self.assertEqual('REQUEST_ERROR', response['response_code'])
        self.assertEqual(1, len(response['errors']))
        self.assertEqual(apilib.CommonErrorCodes.REQUIRED, response['errors'][0]['code'])
        self.assertEqual('operations[0].operand.id', response['errors'][0]['path'])
        self.assertEqual('Field is required on method(s) "delete, mutate/UPDATE, NonwidgetService.get"', response['errors'][0]['message'])

        id_add_request = {'operations': [{'operator': 'ADD', 'operand': {'id': 'foo'}}]}
        response = widget_service.invoke_with_json('delete', id_add_request)
        self.assertIsNotNone(response)
        self.assertEqual('SUCCESS', response.get('response_code'))

        id_set_request = {'operations': [{'operator': 'UPDATE', 'operand': {'id': 'foo'}}]}
        response = widget_service.invoke_with_json('mutate', id_set_request)
        self.assertIsNotNone(response)
        self.assertEqual('SUCCESS', response.get('response_code'))

        id_set_request = {'operations': [{'operator': 'UPDATE', 'operand': {'id': 'foo'}}]}
        response = nonwidget_service.invoke_with_json('get', id_set_request)
        self.assertIsNotNone(response)
        self.assertEqual('SUCCESS', response.get('response_code'))


if __name__ == '__main__':
    unittest.main()
