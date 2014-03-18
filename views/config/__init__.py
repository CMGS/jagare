#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 11:46:56 28/06/2013

from flask import Blueprint
from flask.views import MethodView

from jagare.error import JagareError
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

def foreach_pygit2_config(key, name, lst):
    lst[key] = name
    return 0

class ConfigView(MethodView):

    decorators = [require_project_name("name"), jsonize]

    def get(self, repository, exists):
        config = repository.config
        lst = {}
        config.foreach(foreach_pygit2_config, lst)
        return lst

class GetConfigView(MethodView):

    decorators = [require_project_name("name"), jsonize]

    def get(self, repository, exists, key):
        config = repository.config

        try:
            key in config
        except ValueError:
            raise JagareError("Key error", 404)

        return {"data" : config[key]}

config_view = ConfigView.as_view('config')
get_config_view = GetConfigView.as_view('get')

bp = Blueprint('config', __name__)
bp.add_url_rule('', view_func = config_view, methods = ["GET"])
bp.add_url_rule('/get/<string:key>', view_func = get_config_view, methods = ["GET"])
