apilib
======

A lightweight library for defining JSON APIs in Python.

Apilib allows you to define your API's object hierarchy and types.
Serialization and deserialization between JSON representations and
the Python equivalents are handled automatically. The library
is extensible so that one can define new types with custom serialization
behavior.

One can also declare validation constraints, such as fields that are
required, readonly, or only valid within a given range. The validation
context is flexible enough to declare that certain constraints only
matter for certain API endpoints. For example, the id of an object
may be required on an 'update' call but obviously not required on
an 'insert'. A handful of common validators are provided but any
arbitrary validator can be written.

One of the main goals of apilib is to make APIs self-documenting.
Even with the best of intentions, if one hand-writes documentation
for API fields and their constraints, the behavior the API and its
documentation will drift out of sync. Apilib generates documentation
from the field declarations themselves, so the documentation always
reflects the behavior of the API. (At least as far as serialization
and basic validation concerned; all bets are off if one's endpoint
implementations are wonky.)

Apilib is designed around an RPC model as opposed to a REST model,
but it can be adapted as needed. One typically defines Services
which have one or more methods taking a JSON Request object and
returning a JSON Response object. Typically transport is done
using HTTP POST requests, and each method is represented
but a unique url path. The transport is up to the implementer,
however. The service model is inspired by Google's Protocol Buffers.
The advantage of the RPC model over REST is (1) that Request
objects are easier to specify, using JSON to allow easy nesting
rather than url parameters, and (2) to allow 'multi' requests
more easily, e.g. inserting, updating, or deleting multiple
objects together in the same request. REST APIs typically
allow modifying only one resource at a time and so are a burden
to use for any kind of bulk work.

The syntax is inspired by SQLAlchemy's ORM. An API model's fields
are declared on the class, using descriptors, and a field's name
both for attribute access and serialization is taken to be the name
of the field variable.

## Basic Usage

```python
import apilib

class Person(apilib.Model):
    name = apilib.Field(apilib.String())

p = Person(name='Bob')
p.name           # --> u'Bob'
p.to_json()      # --> {'name': u'Bob'}
p.to_json_str()  # --> '{"name": u"Bob"}'

p = Person.from_json({'name': u'Jim'})
p.name           # --> u'Jim'
```

## Typed Fields

```python
import datetime

class Person(apilib.Model):
    name =  apilib.Field(apilib.String())
    birthday = apilib.Field(apilib.Date())

p = Person(name='Jim', birthday=datetime.date(1977, 4, 3))
p.birthday   # --> datetime.date(1977, 4, 3)
p.to_json()  # --> {'birthday': u'1977-04-03', 'name': u'Jim'}
```

## Complex Models

```python
class Student(apilib.Model):
    name = apilib.Field(apilib.String())

class School(apilib.Model):
    students = apilib.Field(apilib.ListType(Student))

s = School(students=[Student(name='Peter'), Student(name='Jane')])
s.to_json()  # --> {'students': [{'name': u'Peter'}, {'name': u'Jane'}]}
```

## Services

The real goal of apilib is to allow you to define API services that you then implement in Python.
In practice `Models` exist as building blocks to create `Request` and `Response` objects that you
use to define `Services`.

This example defines an abstract API service with a single method and request and response
objects for that method:

```python
class GetStudentsRequest(apilib.Request):
    names = apilib.Field(apilib.ListType(apilib.String()))

class GetStudentsResponse(apilib.Response):
    students = apilib.Field(apilib.ListType(Student))

class StudentService(apilib.Service):
    methods = apilib.servicemethods(
        apilib.MethodDescriptor('get', GetStudentsRequest, GetStudentsResponse))
```

You then need to implement the service. A sample implementation:

```python
class StudentServiceImpl(StudentService, apilib.ServiceImplementation):
    def get(self, req):
        # Query the database using something like sqlalchemy
        db_students = DbStudent.query.filter(DbStudent.name.in_(req.names))
        # Use a helper function that maps database objects to abstract API objects.
        api_students = [db_student_to_api(db_student) for db_student in db_students]
        return GetStudentsResponse(students=api_students)
```

That's a complete service implementation and you can instantiate a `StudentServiceImpl` in code
and call the `get()` method with a valid request object. In practice though, you will want
to register the service as an HTTP endpoint so it can be called remotely. The details of
that will depend on your HTTP server framework, but in general it should be easy to hook
a service implementation into common Python HTTP servers, by making use of the
`invoke_with_json()` method of the `ServiceImplementation` base class.

Here's how you could expose an API service using Flask:

```python
from flask import Flask
from flask import json
from flask import request

app = Flask(__name__)

@app.route('/api/student_service/<method_name>', methods=['POST'])
def student_service(method_name):
    service = StudentServiceImpl()
    response_dict = service.invoke_with_json(method_name, request.json)
    return json.jsonify(response_dict)

```

This means that if you make a POST request to `/api/student_service/get` with payload
that is the JSON representation of a `GetStudentsRequest` object, this route handler
will invoke the `get` method of the service implementation, after deserializing the JSON
object into an actual Python `GetStudentsRequest`. The `invoke_with_json` method will
return a dict primitive representation of the `GetStudentsResponse`, ready for serializing
with `json.jsonify`.
(When making a remote HTTP request to a server framework that is finicky about content types,
like Flask, remember to set `Content-Type: application/json`
in your HTTP request headers, so that Flask will properly populate `request.json`.)

Put more simply, calling `StudentServiceImpl().get(<...>)` takes an `apilib.Request` object and
returns an `apilib.Response` object. Calling `StudentServiceImpl().invoke_with_json('get', <...>)`
takes a dictionary (JSON) primitive of the request object and returns a dictionary (JSON) primitive
of the response object. `invoke_with_json` is a convenience for hooking into HTTP routes that
converts from dict primitive representations of objects and their Python `Request` and `Response`
equivalents for you.

### Best Practices

It's most convenient to assign the root url path of a service with the service definition itself.
This allows you to register HTTP endpoints for services more generically. In Flask, for example:

```python
class StudentService(apilib.Service):
    path = '/api/student_service'
    methods = apilib.servicemethods(...)

class StudentServiceImpl(StudentService, apilib.ServiceImplementation):
    # As before
    ...

#####

from flask import Flask
from flask import json
from flask import request
from flask_user import current_user

app = Flask(__name__)

def serviceroute(service_class):
    return app.route(service_class.path + '/' + '<method_name>', methods=['POST'])

def invoke_service(service_class, method_name, **service_kwargs):
    service = service_class(**service_kwargs)
    response = service.invoke_with_json(method_name, request.json)
    return json.jsonify(response)

@serviceroute(StudentServiceImpl)
def student_service(method_name):
    return invoke_service(StudentServiceImpl, method_name, current_user=current_user)
```

## Full Reference

### Field Types

#### String

Any string of unicode characters. Deserializes to the Python 'unicode' type.

```python
class Foo(apilib.Model):
    name = apilib.Field(apilib.String())

foo = Foo(name='This is a string')
foo.to_json()  # --> {'name': 'This is a string'}
```

#### Integer

An integer. Deserializes to the Python 'int' type Neither Python nor JSON meaningfully distinguish between short, long, or regular integers.

```python
class Foo(apilib.Model):
    value = apilib.Field(apilib.Integer())

foo = Foo(value=98)
foo.to_json()  # --> {'value': 98}
```

#### Float

A floating point number. Deserializes to the Python 'float' type.

```python
class Foo(apilib.Model):
    value = apilib.Field(apilib.Float())

foo = Foo(value=1.25)
foo.to_json()  # --> {'value': 1.25}
```

#### Boolean

A boolean.

```python
class Foo(apilib.Model):
    is_correct = apilib.Field(apilib.Boolean())

foo = Foo(is_correct=True)
foo.to_json()  # --> {'value': True}
foo.to_json_str()  # --> '{"is_correct": true}'

foo = Foo(is_correct=False)
foo.to_json()  # --> {'value': False}
foo.to_json_str()  # --> '{"is_correct": false}'

foo = Foo(is_correct=None)
foo.to_json()  # --> {'value': None}
foo.to_json_str()  # --> '{"is_correct": null}'
```

#### ModelType

A field whose value is another model. The field value will serialize to a JSON object containing the fields of the nested object. Such a JSON object will deserialize into the corresponding Model object.

`ModelType` takes a single argument, which must be a subclass of `apilib.Model`.

```python
class Foo(apilib.Model):
    value = apilib.Field(apilib.String())

class Bar(apilib.Model):
    foo = apilib.Field(apilib.ModelType(Foo))

bar = Bar(foo=Foo(value='hello'))
bar.to_json()  # --> {'foo': {'value': u'hello'}}
```

#### ListType

A field whose value is a list of other values. `ListType` takes a single argument, which must be either a subclass of `apilib.Model` if this is a list of other objects, or an instance of `FieldType` indicating the primitive type contained in this list.

```python
class Foo(apilib.Model):
    list_value = apilib.Field(apilib.ListType(apilib.String()))

foo = Foo(list_value=['foo', 'bar'])
foo.to_json()  # --> {'list_value': [u'foo', u'bar']}

class Bar(apilib.Model):
    name = apilib.Field(apilib.String())

class Baz(apilib.Model):
    list_value = apilib.Field(apilib.ListType(Bar))

baz = Baz(list_value=[Bar(name='Alice'), Bar(name='Bob')])
baz.to_json()  # --> {'list_value': [{'name': u'Alice'}, {'name': u'Bob'}]}
```

Since the argument to `ListType` can be a `FieldType` instance, you can create nested lists and other complex field values.

```python
class Foo(apilib.Model):
    complex_list = apilib.Field(apilib.ListType(apilib.ListType(apilib.String())))

foo = Foo(complex_list=[['a'], ['b', 'c']])
foo.to_json()  # --> {'complex_list': [[u'a'], [u'b', u'c']]}
```

#### DictType

A field whose value is a dictionary with string keys and values of a specified type. `DictType` takes a single argument, which must be either a subclass of `apilib.Model` if this is a dict mapping to other objects, or an instance of `FieldType` indicating the primitive type of the dict's values.

```python
class Foo(apilib.Model):
    dict_value = apilib.Field(apilib.DictType(apilib.String()))

foo = Foo(dict_value={'somekey': 'somevalue'})
foo.to_json()  # --> {'dict_value': {'somekey': u'somevalue'}}

class Bar(apilib.Model):
    name = apilib.Field(apilib.String())

class Baz(apilib.Model):
    dict_value = apilib.Field(apilib.DictType(Bar))

baz = Baz(dict_value={'somekey': Bar(name='Alice')})
baz.to_json()  # --> {'dict_value': {'somekey': {'name': u'Alice'}}}
```

Since the argument to `DictType` can be a `FieldType` instance, you can create nested dicts and other complex field values.

```python
class Foo(apilib.Model):
    complex_dict = apilib.Field(apilib.DictType(apilib.ListType(apilib.String())))

foo = Foo(complex_dict={'somekey': ['a', 'b']})
foo.to_json()  # --> {'complex_dict': {'somekey': [u'a', u'b']}}
```

#### DateTime

A field representing a date and time. In Python, this should be an instance of `datetime.datetime`. This will serialize to a string in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM). The timezone portion (+HH:MM) is optional.

```python
import datetime
from dateutil import tz

class Foo(apilib.Model):
    timestamp = apilib.Field(apilib.DateTime())

timestamp = datetime.datetime(2017, 2, 14, 15, 30,
    tzinfo=tz.gettz('America/Los_Angeles'))
foo = Foo(timestamp=timestamp)
foo.to_json()  # --> {'timestamp': u'2017-02-14T15:30:00-08:00'}

foo = Foo.from_json({'timestamp': u'2017-02-14T15:30:00-08:00'})
foo.timestamp  # --> datetime.datetime(2017, 2, 14, 15, 30, tzinfo=tzoffset(None, -28800))
```

#### Date

A field representing a date. In Python, this should be an instance of `datetime.date`. This will serialize to a string in ISO 8601 format (YYYY-MM-DD).

```python
import datetime

class Foo(apilib.Model):
    date = apilib.Field(apilib.Date())

date = datetime.date(2017, 2, 14)
foo = Foo(date=date)
foo.to_json()  # --> {'date': u'2017-02-14'}

foo = Foo.from_json({'date': u'2017-02-14'})
foo.date  # --> datetime.date(2017, 2, 14)
```

#### Decimal

A field representing a numeric value with accurate decimal precision, e.g. to represent a currency amount. In Python, this should be an instance of decimal.Decimal. This will serialize to a string consisting of the decimal representation of the value, since JSON has no other way to faithfully represent an exact decimal value.

```python
import decimal

class Foo(apilib.Model):
    cost = apilib.Field(apilib.Decimal())

foo = Foo(cost=decimal.Decimal('10.10'))
foo.to_json()  # --> {'cost': u'10.10'}

foo = Foo.from_json({'cost': u'10.10'})
foo.cost  # --> Decimal('10.10')
```

#### Enum

A field containing a fixed number of choices. This is equivalent to a `String` field but with validation during serialization the the given value is valid. `Enum` takes a single argument containing a list of valid values.

```python
class Foo(apilib.Model):
    color = apilib.Field(apilib.Enum(['red', 'green', 'blue']))

foo = Foo(color='blue')
foo.to_json()  # --> {'color': u'blue'}

foo = Foo.from_json({'color': u'blue'})
foo.color  # --> 'blue'

foo = Foo.from_json({'color': u'pink'})
#  --> Raises DeserializationError
```

The `Enum` field type is typically used with the convenience class `EnumValues`, which defines a helper method `values()` that returns all string values defined on the class.

```python
class Color(apilib.EnumValues):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue';

class Foo(apilib.Model):
    color = apilib.Field(apilib.Enum(Color.values()))
```

#### Bytes

Any string of characters. Deserializes to the Python 'bytes' type. Useful for blobs, typically the body of a file.

```python
class Foo(apilib.Model):
    body = apilib.Field(apilib.Bytes())

foo = Foo(body=open('somefile.xyz').read())
foo.to_json()  # --> {'body': '<bytes>'}
```

#### EncryptedId

An integer field that is obfuscated during serialization.

Services implemented using SQL databases typically identify most object types using an autoincrement integer id. When using that database id to identify an object in a public API, you wind up leaking both the number of objects contained in your database (since a user can create a new object and see its id) as well as your rate of growth (since a user can create new objects X days apart and see how much higher the new id is). It is a good practice to obfuscate database ids when they are exposed publicly, either via an explicit API or even implicitly as part of JSON responses to a Javascript client in a web app or to a mobile application (mobile app requests can be inspected by any user by making use of a proxy).

The EncryptedId field largely solves this problem for you without any extra effort. Such fields are always treated as integers in Python as they would if this were an Integer field. However, during serialization, the integer is obfuscated into a string using an encryption key.

To use EncyptedId fields, you must install the `hashids` module (`pip install hashids`), and set an encryption key somewhere in your application's initialization code.

```python
apilib.model.ID_ENCRYPTION_KEY = '<some-key>'
```

An easy way to generate a random key is:

```bash
python -c "import base64; import os; print base64.b64encode(os.urandom(32))"
```

Usage:

```python
class Foo(apilib.Model):
    object_id = apilib.Field(apilib.EncryptedId())

foo = Foo(object_id=123)
foo.to_json()  # --> {'object_id': '2ZeEQAem'}

foo = Foo.from_json({'object_id': '2ZeEQAem'})
foo.object_id  # --> 123
```

#### AnyPrimitive

A field that may contain any JSON primitive (int, float, bool, string, list, dict). This field type generally only needs to be used when creating a list or dict field that can contain values of multiple types or unknown types, and is usually used only as the argument to `ListType` or `DictType`. It essentially just disables type-checking during serialization and deserialization.

```python
class Foo(apilib.Model):
    list_field = apilib.Field(apilib.ListType(apilib.AnyPrimitive()))

foo = Foo(list_field=[1, 'hello', True])
foo.to_json()  # --> {'list_field': [1, 'hello', True]}

foo = Foo.from_json({'list_field': [1, 'hello', True]})
too.list_field  # --> [1, 'hello', True]
```
