from __future__ import absolute_import

from . import model
from . import service
from . import validators as vals

class Operator(object):
    ADD = 'ADD'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

class Operation(model.Model):
    operator = model.Field(model.Enum([Operator.ADD, Operator.UPDATE, Operator.DELETE]), required=True)

    @classmethod
    def make_parent_context(cls, obj, context):
        return context.for_parent(obj, obj.get('operator'))

class OrderingDirection(object):
    ASC = 'ASC'
    DESC = 'DESC'

class OrderingCriterion(model.Model):
    field_name = model.Field(model.String(), required=True)
    direction = model.Field(model.Enum([OrderingDirection.ASC, OrderingDirection.DESC]))

class Ordering(model.Model):
    criteria = model.Field(model.ListType(OrderingCriterion), required=True,
        validators=[vals.UniqueFields('field_name')])

class ResponsePage(service.Response):
    start = model.Field(model.Integer())
    num = model.Field(model.Integer())
    total_results = model.Field(model.Integer())

class Pagination(model.Model):
    start = model.Field(model.Integer(), validators=[vals.Range(0)])
    num = model.Field(model.Integer(), validators=[vals.Range(1)])

class Selector(model.Model):
    # filters = ...
    ordering = model.Field(model.ModelType(Ordering))
    pagination = model.Field(model.ModelType(Pagination))
