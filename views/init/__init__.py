#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  15:36:05 23/05/2013
# MODIFIED: 15:20:00 28/06/2013

'''
InitView
--------

.. autoclass:: InitView
    :members:
'''

from pygit2 import init_repository

from flask import request
from flask import Blueprint
from flask.views import MethodView

from error import JagareError
from utils.flask import make_message_response
from utils.decorators import jsonize
from utils.decorators import require_project_name

class InitView(MethodView):
    '''负责 `git init` 相关操作。'''

    decorators = [require_project_name("name", need_object = False, required = False), jsonize]

    def get(self, repository, exists):
        '''
        **POST** `/<path:name>/init`

        参数：

        .. attribute:: name

            初始化项目请求的名字。

        .. attribute:: not_bare

            (defaults: *False*) 是否不初始化为 bare git 项目, 这个参数包含任何值均会认定为 True 。

        返回值：

        .. attribute:: error

            * 0 - 正确初始化项目。
            * 1 - 初始化失败, 参考 message 参数获得原因。

        .. attribute:: message

            描述错误信息。
        '''

        return make_message_response("initialize success")

init_view = InitView.as_view('init')

bp = Blueprint('init', __name__)
bp.add_url_rule('', view_func = init_view, methods = ['GET','POST'])

__all__ = ["bp"]

