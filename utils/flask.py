#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  14:45:07 28/06/2013
# MODIFIED: 16:40:39 01/07/2013

from __future__ import absolute_import

from flask import json
from flask import make_response
from flask.views import MethodView as _

def make_message_response(message, **kwargs):
    response_dict = {
        "message" : message,
        "error"   : 0,
    }
    response_dict.update(kwargs)
    return make_response(json.jsonify(response_dict), 200)

class MethodView(_):
    def __init__(self, module, tmpl):
        super(MethodView, self).__init__()

    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        def view(*args, **kwargs):
            return view.instance.dispatch_request(*args, **kwargs)

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        view.instance = cls(*class_args, **class_kwargs)
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.methods = cls.methods
        return view
