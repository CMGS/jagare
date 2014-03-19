#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  15:36:05 23/05/2013
# MODIFIED: 15:20:00 28/06/2013

'''
InitView
--------

.. autoclass:: DeleteView
    :members:
'''

import shutil

from flask import Blueprint
from flask.views import MethodView

from jagare.error import JagareError
from jagare.utils.flask import make_message_response
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

class DeleteView(MethodView):
    '''负责 `rm -rf git repo` 相关操作。'''

    decorators = [require_project_name("name", need_object = False, required = False), jsonize]

    def get(self, repository, exists):
        '''
        **POST** `/<path:name>/delete`

        参数：

        .. attribute:: name

            请求的名字。

        返回值：

        .. attribute:: error

            * 0 - 正确删除项目。
            * 1 - 删除失败, 参考 message 参数获得原因。

        .. attribute:: message

            描述错误信息。
        '''

        if not exists:
            raise JagareError("repository not exists.", 409)

        shutil.rmtree(repository)
        return make_message_response("delete success")

delete_view = DeleteView.as_view('delete')

bp = Blueprint('delete', __name__)
bp.add_url_rule('', view_func = delete_view, methods = ['GET'])

__all__ = ["bp"]

