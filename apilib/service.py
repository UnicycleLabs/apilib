from __future__ import absolute_import

import inspect
import logging
import traceback

import requests

from . import exceptions
from . import model
from . import validation

logger = logging.getLogger(__name__)

class ApiError(model.Model):
    code = model.Field(model.String())
    path = model.Field(model.String())
    message = model.Field(model.String())

    def __str__(self):
        return '%s: code: %s, path: %s, message: %s' % (
            type(self).__name__, self.code, self.path, self.message)

class Request(model.Model):
    pass

class Response(model.Model):
    response_code = model.Field(model.String())
    errors = model.Field(model.ListType(ApiError))

class ResponseCode(object):
    SUCCESS = 'SUCCESS'
    SERVER_ERROR = 'SERVER_ERROR'
    REQUEST_ERROR = 'REQUEST_ERROR'

class ApiException(exceptions.ApilibException):
    def __init__(self, response_code=None, errors=()):
        self.response_code = response_code
        self.errors = errors

    def __str__(self):
        return '<%s: %s, errors: %s>' % (type(self).__name__, self.response_code,
            ', '.join(str(e) for e in self.errors))

    @classmethod
    def server_error(cls, errors=(), error_msgs=()):
        api_errors = list(errors) + [ApiError(message=msg) for msg in error_msgs]
        return ApiException(ResponseCode.SERVER_ERROR, api_errors)

    @classmethod
    def request_error(cls, errors=(), error_msgs=()):
        api_errors = list(errors) + [ApiError(message=msg) for msg in error_msgs]
        return ApiException(ResponseCode.REQUEST_ERROR, api_errors)

class MethodDescriptor(object):
    def __init__(self, name, request_class, response_class, public=True):
        self.name = name
        self.request_class = request_class
        self.response_class = response_class
        self.public = public

Meth = MethodDescriptor

def servicemethods(*descriptors):
    return {d.name: d for d in descriptors}

class Service(object):
    '''Usage:
    class FooService(apilib.Service):
        methods = apilib.servicemethods(
            apilib.Meth('foo', FooRequest, FooResponse))
        path = '/foo_service'
    '''
    # The methods offered by this service, a tuple of MethodDescriptor objects
    methods = servicemethods()
    # The path this service will be served from, e.g. '/widget_service'
    path = None
    name = None
    public = None

    def get_name(self):
        if self.name:
            return self.name
        if not hasattr(self, '_name'):
            # Find the first parent class that inherits from Service.
            # Any subclass could use multiple inheritance, so we don't
            # want to select a parent class in a different class hierarchy.
            # Also, one service could inherit from another service, so we want
            # to use the highest Service-subclass in the hierarchy.
            for type_ in inspect.getmro(type(self))[1:]:
                if Service in inspect.getmro(type_):
                    self._name = type_.__name__
                    break
        return self._name

class ServiceImplementation(Service):
    '''Usage:
    class FooServiceImpl(FooService, apilib.ServiceImplementation):
        def foo(self, foo_request):
            return FooResponse(...)
    '''

    def invoke(self, method_name, request):
        self.log_request(method_name, request)

        method_descriptor = self.resolve_method(method_name)
        method = getattr(self, method_descriptor.name)
        try:
            response = method(request)
            response.response_code = ResponseCode.SUCCESS
        except ApiException as e:
            response = method_descriptor.response_class(response_code=e.response_code, errors=e.errors)
        except AssertionError:
            # Re-raise for assertions made in unittests
            raise
        except Exception as e:
            if self.process_unhandled_exception(e):
                raise
            response = method_descriptor.response_class(response_code=ResponseCode.SERVER_ERROR)

        self.log_response(method_name, request, response)
        return response

    def invoke_with_json(self, method_name, json_request):
        method_descriptor = self.resolve_method(method_name)
        error_context = validation.ErrorContext()
        validation_context = validation.ValidationContext(service=self.get_name(), method=method_name)
        request = method_descriptor.request_class.from_json(json_request, error_context, validation_context)
        validation_errors = error_context.all_errors()
        if validation_errors:
            response = method_descriptor.response_class(
                response_code=ResponseCode.REQUEST_ERROR,
                errors=[ApiError(code=ve.code, path=ve.path, message=ve.msg) for ve in validation_errors])
        else:
            response = self.invoke(method_name, request)
        return response.to_json() if response else None

    def resolve_method(self, method_name):
        descriptor = self.methods.get(method_name)
        if not descriptor:
            raise exceptions.MethodNotFoundException('No descriptor for method of name "%s"' % method_name)
        if not hasattr(self, method_name):
            raise exceptions.MethodNotImplementedException('Method "%s" not implemented' % method_name)
        return descriptor

    # Override these methods for custom behavior

    def process_unhandled_exception(self, exception):
        # Do any processing, return True to re-raise the exception, otherwise the exception
        # will be logged and a server error response will be returned.
        return False

    def log_request(self, method_name, request):
        logger.debug('API service request: %s.%s\n%s',
            self.__class__.__name__, method_name, request)

    def log_response(self, method_name, request, response):
        if response.response_code == ResponseCode.SERVER_ERROR:
            logger.error('Server error in API call %s.%s\nRequest:\n%s\nResponse: %s\n%s',
                self.__class__.__name__,
                method_name,
                request.to_json_str() if request else None,
                response.to_json_str() if response else None,
                traceback.format_exc() or '')
        else:
            logger.debug('API service response:\n%s', response)

class RemoteServiceStub(Service):
    '''Usage:
    class RemoteFooService(FooService, apilib.RemoteServiceStub):
        pass

    service = RemoteFooService('https://remoteserver.com')
    foo_response = service.foo(FooRequest(...))
    '''
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def _invoke(self, method_descriptor, request):
        url = '%s%s/%s' % (self.base_url, self.path.rstrip('/'), method_descriptor.name)
        response = requests.post(url, data=request.to_json_str(), headers={'Content-Type': 'application/json'})
        return method_descriptor.response_class.from_json(response.json())

    def __getattr__(self, method_name):
        descriptor = self.methods.get(method_name)
        if not descriptor:
            raise exceptions.MethodNotFoundException('No method named "%s" defined on this service' % method_name)
        return lambda request: self._invoke(descriptor, request)
