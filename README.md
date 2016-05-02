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

Basic Usage
-----------

    import apilib

    class Person(apilib.Model):
        name = apilib.Field(apilib.String())

    p = Person(name='Bob')
    p.name           # --> u'Bob'
    p.to_json()      # --> {'name': u'Bob'}
    p.to_json_str()  # --> '{"name": u"Bob"}'

    p = Person.from_json({'name': u'Jim'})
    p.name           # --> u'Jim'

Typed Fields
------------

    import datetime

    class Person(apilib.Model):
        name =  apilib.Field(apilib.String())
        birthday = apilib.Field(apilib.Date())

    p = Person(name='Jim', birthday=datetime.date(1977, 4, 3))
    p.birthday   # --> datetime.date(1977, 4, 3)
    p.to_json()  # --> {'birthday': u'1977-04-03', 'name': u'Jim'}

Complex Models
--------------

    class Student(apilib.Model):
        name = apilib.Field(apilib.String())

    class School(apilib.Model):
        students = apilib.Field(apilib.ListType(Student))

    s = School(students=[Student(name='Peter'), Student(name='Jane')])
    s.to_json()  # --> {'students': [{'name': u'Peter'}, {'name': u'Jane'}]}
