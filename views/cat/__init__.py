#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 13:18:19 02/07/2013

'''
CatView
-------

.. autoclass:: CatView
    :members:

'''

from flask import request
from flask import Blueprint
from flask.views import MethodView

from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_OBJ_BLOB
from pygit2 import GIT_OBJ_TREE
from pygit2 import GIT_OBJ_COMMIT

from jagare.error import JagareError
from jagare.utils.git import format_tag
from jagare.utils.git import format_blob
from jagare.utils.git import format_tree
from jagare.utils.git import format_commit
from jagare.utils.git import PYGIT2_OBJ_TYPE
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

class Cat(object):
    def cat_by_ref(self, repository, ref, only_type=False):
        try:
            obj = repository.revparse_single(ref)
        except KeyError:
            raise JagareError("bad sha value.", 400)
        objtype = obj.type

        if only_type:
            return {"type" : PYGIT2_OBJ_TYPE.get(objtype)}

        if objtype == GIT_OBJ_COMMIT:
            return format_commit(ref, obj, repository)
        elif objtype == GIT_OBJ_TAG:
            return format_tag(ref, obj, repository)
        elif objtype == GIT_OBJ_TREE:
            return format_tree(ref, obj, repository)
        elif objtype == GIT_OBJ_BLOB:
            return format_blob(ref, obj, repository)

class CatByPath(MethodView):

    decorators = [require_project_name("name"), jsonize]

    def get(self, repository, exists, ref):
        req_path = request.args.get("path", None)
        only_type = request.args.get("only_type", False)

        commit = repository.revparse_single(ref)
        tree = commit.tree

        try:
            entry = tree[req_path] if req_path else tree
            obj = repository[entry.hex]
        except (KeyError, ValueError):
            raise JagareError("request path not found.", 400)
        if only_type:
            return {"type" : PYGIT2_OBJ_TYPE.get(obj.type)}
        if obj.type != GIT_OBJ_BLOB:
            raise JagareError("not a blob obj.", 400)
        return format_blob(ref, obj, repository)

class CatView(MethodView):

    decorators = [require_project_name("name"), jsonize]

    def get(self, repository, exists, ref):
        '''
        **GET** `/<path:name>/cat/<path:ref>`

        参数：

        .. attribute:: ref

        需要被 cat 的东西的 SHA 值或 Reference 名。

        .. attribute:: only_type

        （默认值： False）

        只返回 SHA 代表对象类型。

        '''

        only_type = request.args.get("only_type", False)
        cat = Cat()
        ret = cat.cat_by_ref(repository, ref, only_type)
        if not ret:
            raise JagareError("object type is unknown.", 400)
        return ret

cat_view = CatView.as_view('cat')
cat_by_path_view = CatByPath.as_view('cat_by_path')

bp = Blueprint('cat', __name__)
bp.add_url_rule('/<path:ref>', view_func = cat_view, methods = ["GET"])
bp.add_url_rule('/path/<path:ref>', view_func = cat_by_path_view, methods = ["GET"])
