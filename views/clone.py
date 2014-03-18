#!/usr/bin/python
#coding:utf-8

import os
import config

from flask import Blueprint

from ellen.repo import Jagare
from error import JagareError

from utils.git import endwith_git

from utils.flask import MethodView
from utils.flask import make_message_response

from utils.decorators import jsonize
from utils.decorators import require_project_name

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

        if exists:
            raise JagareError("repository already exists", 409)

        jagare = Jagare(clone_path)
        jagare.clone(target_path, bare=True)

        return make_message_response("clone success")

clone_view = CloneView.as_view('clone')

bp = Blueprint('clone', __name__)
bp.add_url_rule('/<path:clone_from>', view_func = clone_view, methods = ['POST'])

__all__ = ["bp"]

