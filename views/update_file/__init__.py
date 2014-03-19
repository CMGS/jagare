#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 16:11:59 28/06/2013

from flask import request
from flask import Blueprint
from flask.views import MethodView

import pygit2 as g

from jagare.error import JagareError
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

def _get_pygit2_mode(mode):
    if mode == "100755":
        return g.GIT_FILEMODE_BLOB_EXECUTABLE
    return g.GIT_FILEMODE_BLOB

def update_files(repository, branch, parent, mode, author_name, author_email, message, data):
    if repository.is_empty:
        if branch != "master" or parent != "master":
            raise JagareError("only commit to master when repo is empty", 400)

    commit_parent = []
    if repository.is_empty:
        bld = repository.TreeBuilder()
        tree = None
    else:
        parent = repository.revparse_single(parent)
        bld = repository.TreeBuilder(parent.tree)
        commit_parent.append(parent.hex)
        tree = parent.tree

    ret = []
    flag = False
    for filepath, content in data.iteritems():
        content = unicode_to_utf8(content.read())
        content = content.replace("\r\n", "\n")
        if content:
            filepath = unicode_to_utf8(filepath)
            mode = _get_pygit2_mode(mode)
            if tree:
                try:
                    entry = tree[filepath]
                    h = g.hash(content).hex
                    if entry.hex == h:
                        continue
                except (KeyError, ValueError):
                    pass
            newfile_oid = repository.write(g.GIT_OBJ_BLOB, content)
            bld.insert(filepath, newfile_oid, g.GIT_FILEMODE_BLOB)
            ret.append(newfile_oid)
            flag = True
        else:
            bld.remove(filepath)
            flag = True

    if flag:
        tree_oid = bld.write()
        signature = g.Signature(author_name, author_email)
        commit = repository.create_commit("refs/heads/%s" % branch, signature, signature, message, tree_oid, commit_parent)
        master = repository.lookup_reference("refs/heads/%s" % branch)
        master.target = commit.hex
        return ret
    return []

def unicode_to_utf8(c):
    if isinstance(c, unicode):
        c = c.encode('utf8')
    return c

class UpdateFileView(MethodView):

    decorators = [require_project_name("name", require_not_empty = False), jsonize]

    def put(self, repository, exists):
        message = request.form.get("message", "")
        branch = request.form.get("branch", "master")
        parent = request.form.get("parent", "master")
        mode = request.form.get("mode", "100644")
        author_name = request.form.get("author_name", "titan")
        author_email = request.form.get("author_email", "titan@titan.com")

        ret = update_files(repository, branch, parent, mode, author_name, author_email, message, request.files)
        # TODO: add reflog. (pygit2 doesn't support yet)
        return [o.hex for o in ret]

update_file_view = UpdateFileView.as_view('update_file')

bp = Blueprint('update_file', __name__)
bp.add_url_rule('/', view_func = update_file_view, methods = ["PUT"])

