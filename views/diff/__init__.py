#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 11:49:18 28/06/2013

from flask.views import MethodView
from flask import Blueprint,request

import pygit2 as g

from jagare.error import JagareError
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

class Diff(object):

    def diff_between_empty(self, repository, from_sha, **kwargs):
        from_tree = self.get_from_tree(repository, from_sha)
        diff = from_tree.diff_to_tree(**kwargs)
        return diff.patch

    def diff_between_commits(self, repository, from_sha, to_sha=None, **kwargs):
        from_tree = self.get_from_tree(repository, from_sha)
        to_tree = self.get_to_tree(repository, from_sha, to_sha)

        if to_tree:
            if from_tree.hex == to_tree.hex:
                raise JagareError("from tree is same with to tree", 400)
            diff = repository.diff(from_tree, to_tree, **kwargs)
            diff.find_similar()
        else:
            diff = from_tree.diff_to_tree(swap=True, **kwargs)
        return diff.patch

    def get_from_tree(self, repository, from_sha):
        try:
            from_commit = repository[from_sha]
        except (ValueError, KeyError):
            raise JagareError("`from_sha` is invalid.", 404)

        if from_commit and from_commit.type == g.GIT_OBJ_TREE:
            from_tree = from_commit
        elif from_commit and from_commit.type == g.GIT_OBJ_COMMIT:
            from_tree = from_commit.tree
        else:
            raise JagareError("Cant find tree object using the sha.", 404)

        return from_tree

    def get_to_tree(self, repository, from_sha, to_sha):
        if not to_sha:
            try:
                from_commit = repository[from_sha]
            except (ValueError, KeyError):
                raise JagareError("`from_sha` is invalid.", 404)

            parents = from_commit.parents
            if len(parents) == 0:
                to_tree = None
            else:
                parent = parents[0]
                to_tree = parent.tree
        else:
            try:
                to_commit = repository[to_sha]
            except (ValueError, KeyError):
                raise JagareError("`to_sha` is invalid", 404)

            if to_commit.type == g.GIT_OBJ_TREE:
                to_tree = to_commit
            elif to_commit.type == g.GIT_OBJ_COMMIT:
                to_tree = to_commit.tree
            else:
                raise JagareError("Cant find tree object using the sha.", 404)

        return to_tree

class DiffView(MethodView):
    decorators = [require_project_name("name"), jsonize]
    def get(self, repository, exists, from_sha, to_sha = None):
        diff = Diff()
        if request.args.get('empty', None):
            return diff.diff_between_empty(repository, from_sha, swap=True)
        return diff.diff_between_commits(repository, from_sha, to_sha)

diff_view = DiffView.as_view('diff')

bp = Blueprint('diff', __name__)
bp.add_url_rule('/<string:from_sha>', view_func = diff_view, methods = ["GET"])
bp.add_url_rule('/<string:from_sha>/<string:to_sha>', view_func = diff_view, methods = ["GET"])
