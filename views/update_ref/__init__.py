#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:33:51 03/06/2013
# MODIFIED: 15:30:42 28/06/2013

'''
UpdateRefView
-------------

.. autoclass:: UpdateRefView
    :members:
'''

from flask import request
from flask import Blueprint
from flask.views import MethodView

from pygit2 import GIT_REF_OID, GIT_REF_SYMBOLIC

from jagare.error import JagareError
from jagare.utils.flask import make_message_response
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

class UpdateRefView(MethodView):
    '''`git update-ref` 相关操作。'''

    decorators = [require_project_name("name"), jsonize]

    def put(self, repository, exists, ref):
        '''
        **PUT** `/<path:name>/update-ref/<path:ref>`

        参数：
        
        .. attribute:: ref
            
            Reference 名称。
        
        .. attribute:: newvalue

            更新之后的值。

        '''
        # TODO: support for no-deref option
        # git update-ref
        if repository.is_empty:
            raise JagareError("repository is empty", 406)

        newvalue = request.form["newvalue"]

        try:
            commit = repository.revparse_single(newvalue)
        except KeyError:
            raise JagareError("newvalue is invalid.", 400)
        except Exception:
            raise JagareError("refs not found.", 400)

        try:
            repo_ref = repository.lookup_reference(ref)
        except KeyError:
            repository.create_reference(ref, commit.hex)
            return make_message_response("update success")

        if repo_ref.type == GIT_REF_OID:
            try:
                repo_ref.target = commit.hex
            except OSError:
                raise JagareError("OSError occurred because of concurrency, try again later", 409)

        # TODO: change acting when the reference is symbolic
        elif repo_ref.type == GIT_REF_SYMBOLIC:
            # WARNING: this else is acting like `git symbolic-ref`
            try:
                repo_new = repository.lookup_reference(newvalue)
            except Exception:
                raise JagareError("refs not found.", 400)
            repo_ref.target = repo_new.name

        return make_message_response("update success")


    def delete(self, repository, exists, ref):
        '''
        **DELETE** `/<path:name>/update-ref/<path:ref>`

        参数：

        .. attribute:: ref

            Reference 名称。

        .. attribute:: oldvalue

            （非必须选项）

            删除名称为 ref 并且值为 oldvalue 的索引。
        '''
        # git update-ref -d 
        if repository.is_empty:
            raise JagareError("repository is empty", 406)
        
        oldvalue = request.args.get("oldvalue")

        try:
            repo_ref = repository.lookup_reference(ref)
        except ValueError:
            raise JagareError("reference not found", 404)
        target = repo_ref.target

        if repo_ref.type == GIT_REF_OID:

            if oldvalue:
                try:
                    commit = repository.revparse_single(oldvalue)
                except KeyError:
                    raise JagareError("delete failed: <oldvalue> is invalid.", 400)

                if target.hex == commit.hex:
                    repo_ref.delete()
                else:
                    raise JagareError("delete failed: <oldvalue> is not current value.", 400)
            else:
                repo_ref.delete()

            return make_message_response("delete success")

        # TODO: 
        #elif repo_ref.type == GIT_REF_SYMBOLIC:

        #    if target == newvalue:
        #        repo_ref.delete()

        #        return {"message" : "delete success", "error" : "0"}

        raise JagareError("reference not found", 404)

update_ref_view = UpdateRefView.as_view('update_ref')

bp = Blueprint('update_ref', __name__)
bp.add_url_rule('/<path:ref>', view_func = update_ref_view, methods = ["PUT", "DELETE"])
