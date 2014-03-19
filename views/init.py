#!/usr/bin/python
#coding:utf-8

import os
import config

from flask import Blueprint

from ellen.repo import Jagare
from error import JagareError

from utils.flask import MethodView
from utils.flask import make_message_response

from utils.git import endwith_git
from utils.git import is_repository
# from utils.decorators import jsonize

class InitView(MethodView):
    decorators = []
    def post(self, name):
        repository_path = os.path.join(config.REPOS_PATH, name)
        repository_path = endwith_git(repository_path)

        repository_exist = is_repository(repository_path)

        if repository_exist:
            raise JagareError("repository already exists.", 409)

        Jagare.init(repository_path)

        return make_message_response("initialize success")
#
#        '''
#        **POST** `/<path:name>/init`
#
#        参数：
#
#        .. attribute:: name
#
#            初始化项目请求的名字。
#
#        .. attribute:: not_bare
#
#            (defaults: *False*) 是否不初始化为 bare git 项目, 这个参数包含任何值均会认定为 True 。
#
#        返回值：
#
#        .. attribute:: error
#
#            * 0 - 正确初始化项目。
#            * 1 - 初始化失败, 参考 message 参数获得原因。
#
#        .. attribute:: message
#
#            描述错误信息。
#        '''
#        repository_path = repository
#        bare = False if request.form.get('not_bare', False) else True
#        if exists:
#            raise JagareError("repository already exists.", 409)
#
#        Jagare.init(repository_path, bare=bare)
#
#        return make_message_response("initialize success")
#
init_view = InitView.as_view('init')

bp = Blueprint('init', __name__)
bp.add_url_rule('', view_func = init_view, methods = ['POST'])

__all__ = ["bp"]
