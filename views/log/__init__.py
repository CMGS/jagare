#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 12:10:46 28/06/2013

'''
LogView
-------

.. autoclass:: LogView
    :members:

'''

from flask import request
from flask import Blueprint
from flask.views import MethodView

from pygit2 import GIT_SORT_TIME
from pygit2 import GIT_SORT_REVERSE
from pygit2 import GIT_DIFF_REVERSE

from jagare.error import JagareError
from jagare.utils.git import _resolve_version
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

class LogView(MethodView):

    decorators = [require_project_name("name"), jsonize]

    def get(self, repository, exists):
        '''
        **GET** `/<path:name>/log`

        参数：
        
        .. attribute:: reference

            (默认值： HEAD)

            从何时开始回溯日志。

        .. attribute:: from_ref

            （非必须选项）

            回溯到何时的日志。

        .. attribute:: shortstat
            
            （非必须选项）

            commit 信息是否显示为简洁类型。

        .. attribute:: no_merges

            （非必须选项）

            是否返回 Merge 的 Commit 信息。

        .. attribute:: reverse

            （非必须选项）

            是否倒序显示。
        '''
        reference = request.args.get("reference", "HEAD")
        from_ref  = request.args.get("from_ref", None)
        shortstat = request.args.get("shortstat", False)
        no_merges = request.args.get("no_merges", False)
        reverse   = request.args.get("reverse", False)

        if shortstat:
            shortstat = True

        if no_merges:
            no_merges = True

        if reverse:
            reverse = True

        sha = _resolve_version(repository, reference)

        if not sha:
            raise JagareError("SHA should target to a tag or a commit object.", 400)

        sort = GIT_SORT_TIME
        if reverse:
            sort |= GIT_SORT_REVERSE

        commits = []
        walker = repository.walk(sha, sort)
        if from_ref:
            from_sha = _resolve_version(repository, from_ref)
            if not from_sha:
                return commits
            walker.hide(from_sha)
        
        for commit in walker:
            _commit = {}
            if no_merges:
                parents = commit.parents
                if parents and len(parents) > 1:
                    continue

            if shortstat:
                parents = commit.parents
                if len(parents) == 0:
                    opt = GIT_DIFF_REVERSE
                    diff = commit.tree.diff(flags=opt, empty_tree=True)
                else:
                    parent = parents[0]
                    diff = parent.tree.diff(commit.tree)
                patches = [p for p in diff]
                additions = 0
                deletions = 0
                changed_files = len(patches)
                for p in patches:
                    additions += p.additions
                    deletions += p.deletions
                _commit['additions'] = additions
                _commit['deletions'] = deletions
                _commit['files'] = changed_files

            _commit['sha'] = commit.hex
            _commit['author_time'] = commit.author.time
            _commit['committer_time'] = commit.committer.time
            _commit['author_name'] = commit.author.name
            _commit['author_email'] = commit.author.email
            _commit['message'] = commit.message
            commits.append(_commit)
        return commits


log_view = LogView.as_view('log')

bp = Blueprint('log', __name__)
bp.add_url_rule('', view_func = log_view, methods = ["GET"])
