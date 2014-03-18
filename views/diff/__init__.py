#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 11:49:18 28/06/2013

from flask import Blueprint
from flask.views import MethodView

import pygit2 as g

from jagare.error import JagareError
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

class DiffView(MethodView):

    decorators = [require_project_name("name"), jsonize]

    def get(self, repository, exists, from_sha, to_sha = None):
        try:
            from_commit = repository[from_sha]
        except ValueError:
            raise JagareError("`from_sha` is invalid.", 404)

        if to_sha:
            try:
                to_commit = repository[to_sha]
            except ValueError:
                raise JagareError("`to_sha` is invalid", 404)
            
            if to_commit.type == g.GIT_OBJ_TREE:
                to_tree = to_commit
            elif to_commit.type == g.GIT_OBJ_COMMIT:
                to_tree = to_commit.tree
            else:
                raise JagareError("Cant find tree object using the sha.", 404)
        else:
            to_commit = repository[repository.head.target.hex]
            to_tree = to_commit.tree

        if from_commit and from_commit.type == g.GIT_OBJ_TREE:
            from_tree = from_commit
        elif from_commit and from_commit.type == g.GIT_OBJ_COMMIT:
            from_tree = from_commit.tree
        else:
            raise JagareError("Cant find tree object using the sha.", 404)

        if from_tree.hex == to_tree.hex:
            raise JagareError("from tree is same with to tree", 400)
        
        diff = from_tree.diff(to_tree)

        return diff.patch

diff_view = DiffView.as_view('diff')

bp = Blueprint('diff', __name__)
bp.add_url_rule('/<string:from_sha>', view_func = diff_view, methods = ["GET"])
bp.add_url_rule('/<string:from_sha>/<string:to_sha>', view_func = diff_view, methods = ["GET"])
