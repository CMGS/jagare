#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 11:41:44 03/06/2013

from flask import Blueprint
from flask.views import MethodView

class BaseView(MethodView):

    decorators = []

    def get(self):
        pass

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

base_view = BaseView.as_view('base')

bp = Blueprint('_base', __name__)
bp.add_url_rule('/', view_func = base_view, methods = ["GET"])

