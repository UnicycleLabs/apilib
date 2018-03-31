# Utilities for inspecting model and service objects. Can be used
# to find the transitive closure of all objects used by a service,
# for example when generating API documentation.

from __future__ import absolute_import

import six

def get_model_classes_from_services(service_classes, public_only=False):
    model_classes = set()
    for service_class in service_classes:
        if public_only and not service_class.public:
            continue
        model_classes.update(get_model_classes_from_service(service_class, public_only))
    return model_classes

def get_model_classes_from_service(service_class, public_only=False):
    model_classes = set()
    for descriptor in six.itervalues(service_class.methods):
        if public_only and not descriptor.public:
            continue
        for model_class in [descriptor.request_class, descriptor.response_class]:
            model_classes.add(model_class)
            model_classes.update(get_model_classes_from_model(model_class))
    return model_classes

def get_model_classes_from_model(model_class):
    model_classes = set()
    model_class.init()
    for field in model_class.get_fields():
        # This is only non-null if this is a complex type, like a List of a Model.
        field_model_class = get_model_class_from_field_type(field.get_type())
        if field_model_class:
            field_model_class.init()
            model_classes.add(field_model_class)
            model_classes.update(get_model_classes_from_model(field_model_class))
    return model_classes

def get_model_class_from_field_type(field_type):
    if hasattr(field_type, 'get_model_class'):
        return field_type.get_model_class()
    elif hasattr(field_type, 'get_item_type'):
        return get_model_class_from_field_type(field_type.get_item_type())
    return None
