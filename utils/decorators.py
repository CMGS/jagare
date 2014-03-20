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
from flask import Response
from flask import make_response

from ellen.repo import Jagare

from error import JagareError
from utils.git import endwith_git
from utils.git import is_repository

def jsonize(func):
    '''将函数返回的字典转化为 json 字符串。'''
    @wraps(func)
    def _(*a, **kw):
        retval = func(*a, **kw)
        if isinstance(retval, Response):
            return retval
        retdict = {
            "data" : retval,
            "error" : False
        }
        return make_response(json.jsonify(retdict))

    return _

def require_repository(func):
    @wraps(func)
    def _(*w, **kw):
        repository_name = kw.pop("name") if kw.has_key("name") else None
        
        if not repository_name:
            raise JagareError("Repository name is required.", 400)
        
        repository_path = os.path.join(config.REPOS_PATH, repository_name)
        repository_path = endwith_git(repository_path)
        repository_exist = is_repository(repository_path)
    
        if not repository_exist:
            raise JagareError("Repository not found.", 404)
    
        repository = Jagare(repository_path)
    
        return func(repository = repository, *w, **kw)
    return _
