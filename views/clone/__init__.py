#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  17:15:04 29/05/2013
# MODIFIED: 15:19:03 28/06/2013

'''
CloneView
---------

.. autoclass:: CloneView
    :members:

'''

import os
import config

from flask import abort
from flask import Blueprint
from flask.views import MethodView

from pygit2 import is_repository
from pygit2 import clone_repository

from jagare.error import JagareError
from jagare.utils.git import endwith_git
from jagare.utils.flask import make_message_response
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

class CloneView(MethodView):
    '''`git clone` 操作。'''
    
    decorators = [require_project_name("name", need_object = False, required = False), jsonize]
    
    def post(self, repository, exists, clone_from):
        '''
        **POST** `/<path:name>/clone/<path:clone_from>`

        参数：

        .. attribute:: name

            clone 到的目标目录名。

        .. attribute:: clone_from

            clone 的项目地址。
        '''
        target_path = repository

        clone_path = os.path.join(config.REPOS_PATH, clone_from)
        clone_path = endwith_git(clone_path)

        if not is_repository(clone_path):
            return abort(404)

        if exists:
            raise JagareError("repository already exists", 409)

        clone_repository(clone_path, target_path, bare = True)
        
        return make_message_response("clone success")

clone_view = CloneView.as_view('clone')

bp = Blueprint('clone', __name__)
bp.add_url_rule('/<path:clone_from>', view_func = clone_view, methods = ['POST'])

__all__ = ["bp"]
