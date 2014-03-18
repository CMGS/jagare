#!/usr/bin/python
#coding:utf-8

from flask import request
from flask import Blueprint

from ellen.repo import Jagare
from error import JagareError

from utils.flask import MethodView
from utils.flask import make_message_response

from utils.decorators import jsonize
from utils.decorators import require_project_name

class InitView(MethodView):
    decorators = [require_project_name("name", need_object = False, required = False), jsonize]
    def post(self, repository, exists):
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
        repository_path = repository
        bare = False if request.form.get('not_bare', False) else True
        if exists:
            raise JagareError("repository already exists.", 409)

        Jagare.init(repository_path, bare=bare)

        return make_message_response("initialize success")

init_view = InitView.as_view('init')

bp = Blueprint('init', __name__)
bp.add_url_rule('', view_func = init_view, methods = ['POST'])

__all__ = ["bp"]
