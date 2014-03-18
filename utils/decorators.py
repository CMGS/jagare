#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  15:50:20 23/05/2013
# MODIFIED: 13:18:58 02/07/2013

'''
decorators
----------

.. autofunction:: jsonize

.. autoclass:: require_project_name
'''

from __future__ import absolute_import

import os
import config
from functools import wraps

from flask import json
from flask import request
from flask import Response
from flask import make_response

from pygit2 import is_repository

from error import JagareError
from utils.git import endwith_git
from utils.git import GitRepository

def jsonize(func):
    '''将函数返回的字典转化为 json 字符串。'''
    @wraps(func)
    def _(*a, **kw):
        try:
            retval = func(*a, **kw)
        except JagareError as e:
            return e.make_response()

        if isinstance(retval, str) or isinstance(retval, unicode):
            return retval
        elif isinstance(retval, Response):
            return retval
        elif isinstance(retval, list):
            retval = {"data" : retval, "error" : 0}
        elif isinstance(retval, dict):
            if "data" not in retval or \
                    not isinstance(retval["data"], (list, dict)):
                retval = {"data" : retval, "error" : 0}

        return make_response(json.jsonify(retval))

    return _

class require_project_name(object):
    """
    修饰器，从指定的请求名中解析出 repository 对象。

    参数：

    .. attribute:: name

        在这个请求中表达 repository name 的键名。

    .. attribute:: required

        *(defaults: False)*

        参数为 `True` 时获取仓库失败则直接返回 `400 Bad Request` ，参数为 `False` 时则将仓库路径返回给 View 函数。

    .. attribute:: need_object

        *(defaults: False)*

        参数为 `True` 时，会将 `Repository` 对象返回给 View 函数，参数为 `False` 时则将仓库路径返回给 View 函数。 

        `True` 参数仅在仓库存在时工作。

    返回值：

    .. attribute:: repository

        根据 `need_object` 参数返回 `Repository` 对象或 `repository_path` 。

    .. attribute:: exists

        仓库是否存在。

    """

    def __init__(self, name, required = True, need_object = True, require_not_empty=True):
        self.name = name
        self.required = required
        self.need_object = need_object
        self.require_not_empty = require_not_empty

    def __call__(self, func):
        @wraps(func)
        def _(*w, **kw):
            if kw.has_key(self.name):
                repository_name = kw.pop(self.name)
            elif request.method in ["PUT", "POST", "PATCH"]:
                repository_name = request.form.get(self.name, None)
            else:
                repository_name = request.args.get(self.name, None)

            if repository_name == None:
                raise JagareError("`%s` is required." % self.name, 400)

            permdir_path = config.REPOS_PATH

            repository_path = os.path.join(permdir_path, repository_name)
            repository_path = endwith_git(repository_path)

            repository_exist = is_repository(repository_path)
            if repository_exist:
                repository = GitRepository(repository_path)
                if repository.is_empty and self.require_not_empty and self.required:
                    raise JagareError("Repository is empty", 500)
                if self.need_object:
                    return func(repository = repository, exists = True, *w, **kw)
                return func(repository = repository_path, exists = True, *w, **kw)
            else:
                if self.required:
                    raise JagareError("Repository not found.", 404)
                return func(repository = repository_path, exists = False, *w, **kw)
        return _
