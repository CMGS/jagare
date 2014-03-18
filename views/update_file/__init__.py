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
from jagare.utils.flask import make_message_response
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

TEMP_BRANCH_MARKER = "TEMP_BRANCH"

class UpdateFileView(MethodView):

    decorators = [require_project_name("name", require_not_empty = False), jsonize]

    @staticmethod
    def _get_pygit2_mode(mode):
        if mode == "100755":
            return g.GIT_FILEMODE_BLOB_EXECUTABLE
        return g.GIT_FILEMODE_BLOB

    def put(self, repository, exists, filepath):
        source_file = request.files['source']
        message = request.form.get("message", "")
        branch = request.form.get("branch", "master")
        parent = request.form.get("parent", "master")
        mode = request.form.get("mode", "100644")
        author_name = request.form.get("author_name", "Code")
        author_email = request.form.get("author_email", "code@douban.com")

        source = source_file.stream.read()

        tmp_new_branch = branch.startswith("patch_tmp")

        if tmp_new_branch:
            reflog_msg = TEMP_BRANCH_MARKER
        else:
            reflog_msg = "commit one file on %s" % branch

        if repository.is_empty:
            if branch != "master" or parent != "master":
                raise JagareError("only commit to master when repo is empty", 400)

        mode = self._get_pygit2_mode(mode)
        newfile_oid = repository.write(g.GIT_OBJ_BLOB, source.replace("\r\n", "\n"))

        commit_parent = []

        if repository.is_empty:
            bld = repository.TreeBuilder()
        else:
            parent = repository.revparse_single(parent)
            bld = repository.TreeBuilder(parent.tree)
            commit_parent.append(parent.hex)

        bld.insert(filepath, newfile_oid, g.GIT_FILEMODE_BLOB)

        tree_oid = bld.write()
        signature = g.Signature(author_name, author_email)

        commit = repository.create_commit("refs/heads/%s" % branch, signature, signature, message, tree_oid, commit_parent)

        master = repository.lookup_reference("refs/heads/%s" % branch)
        master.target = commit.hex

        # TODO: add reflog. (pygit2 doesn't support yet)

        return make_message_response("updated success!", sha = newfile_oid.hex)

update_file_view = UpdateFileView.as_view('update_file')

bp = Blueprint('update_file', __name__)
bp.add_url_rule('/<path:filepath>', view_func = update_file_view, methods = ["PUT"])
