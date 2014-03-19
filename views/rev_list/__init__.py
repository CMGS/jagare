#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 11:21:15 28/06/2013

from flask import request
from flask import Blueprint
from flask.views import MethodView

from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_SORT_TIME

from jagare.error import JagareError
from jagare.utils.git import format_commit
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

class RevListView(MethodView):

    decorators = [require_project_name("name"), jsonize]
    
    def check_author(self, commit, author):
        if author and commit.author.name == author:
            return True
        elif author and commit.author.email == author:
            return True
        elif not author:
            return True
        return False

    def check_path(self, tree, path):
        try:
            entry = tree[path]
        except KeyError:
            return None
        return entry

    # FIXME: add quick diff
    def check_file_change(self, commit, path):
        commit_tree = commit.tree
        parents = commit.parents
        if path and self.check_path(commit_tree, path):
            count = 0
            c_entry = commit_tree[path]
            for p in parents:
                parent_tree = p.tree
                if commit_tree.oid == parent_tree.oid:
                    return False
                p_entry = self.check_path(parent_tree, path)
                if not p_entry:
                    count += 1
                    continue
                if p_entry.oid != c_entry.oid:
                    count += 1
            if count == len(parents):
                return True
        elif not path:
            return True

    def get(self, repository, exists, to_ref):

        from_ref = request.args.get("from_ref", None)
        path = request.args.get("path", None)
        skip = request.args.get("skip", 0)
        max_count = request.args.get("max_count", 20)
        author = request.args.get("author", None)

        try:
            skip = int(skip)
            max_count = int(max_count)
        except ValueError:
            raise JagareError("skip or max_count must be an integer", 400)

        if repository.is_empty:
            return []

        commits_index_list = []
        commits_dict = {}
        to_commit = repository.revparse_single(to_ref)

        if to_commit.type == GIT_OBJ_TAG:
            to_commit = repository[to_commit.target]
        walker = repository.walk(to_commit.oid, GIT_SORT_TIME)
        if from_ref:
            try:
                from_commit = repository.revparse_single(from_ref)
                if from_commit.type == GIT_OBJ_TAG:
                    from_commit = repository[from_commit.target]
                walker.hide(from_commit.oid)
            except (KeyError, ValueError):
                from_commit = None

        if max_count:
            length = max_count + skip if skip else max_count
        else:
            length = 0
        for c in walker:
            if all([self.check_author(c, author),
                    self.check_file_change(c, path)]):
                index = c.hex
                if index not in commits_index_list:
                    commits_index_list.append(index)
                commits_dict[index] = c
            if length and len(commits_index_list) >= length:
                break
        if skip:
            commits_index_list = commits_index_list[skip:]
        return [format_commit(i, commits_dict[i], repository) for i in commits_index_list]

rev_list_view = RevListView.as_view('rev_list')

bp = Blueprint('rev_list', __name__)
bp.add_url_rule('/<path:to_ref>', view_func = rev_list_view, methods = ["GET"])
