#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  23:29:15 28/05/2013
# MODIFIED: 13:18:03 02/07/2013

'''
git
---

.. autofunction:: endwith_git

.. autofunction:: format_pygit2_signature

.. autofunction:: _resolve_version
'''

from __future__ import absolute_import

import magic
from datetime import datetime

from flask import Response, stream_with_context

from pygit2 import Repository
from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_OBJ_BLOB
from pygit2 import GIT_OBJ_TREE
from pygit2 import GIT_OBJ_COMMIT

from error import JagareError
from utils.date import FixedOffset

PYGIT2_OBJ_TYPE = {
    GIT_OBJ_COMMIT: 'commit',
    GIT_OBJ_BLOB: 'blob',
    GIT_OBJ_TREE: 'tree',
    GIT_OBJ_TAG: 'tag',
}

def endwith_git(path):
    """给不以 .git 结尾的路径添加 .git 后缀。"""
    if not path.endswith(".git"):
        path = path + ".git"
    return path

def format_pygit2_signature(signature):
    # copy from http://code.dapps.douban.com/code/blob/f37dbf0a51a783fa3af14574a4379dd6e2d64b35/libs/git2.py#L-25
    '''格式化 pygit2 操作人信息'''
    d = {}
    d['date'] = datetime.fromtimestamp(
        signature.time,
        # FIXME: add offset for app.
        # FixedOffset(signature.offset, None)
    )
    d['name'] = signature.name
    d['email'] = signature.email
    # strftime('%Y-%m-%dT%H:%M:%S+0800')
    d['ts'] = str(signature.time)
    d['tz'] = datetime.fromtimestamp(signature.time, FixedOffset(signature.offset, None)).strftime('%z')
    return d

def _resolve_version(repository, version):
    '''返回完整的 40 位的 commit hash '''
    if len(version) == 40:
        return version
    try:
        obj = repository.revparse_single(version)
        if obj.type == GIT_OBJ_TAG:
            commit = repository[obj.target]
        elif obj.type == GIT_OBJ_COMMIT:
            commit = obj
        elif obj.type == GIT_OBJ_BLOB:
            return None
        elif obj.type == GIT_OBJ_TREE:
            return None
    except KeyError:
        raise JagareError("version not found", 400)
    return commit.hex

def format_short_reference_name(name):
    short = ''
    if name.startswith('refs/heads/'):
        short = name[11:]
    elif name.startswith('refs/remotes/'):
        short = name[13:]
    elif name.startswith('refs/tags/'):
        short = name[10:]
    elif name.startswith('refs/'):
        short = name[5:]
    else:
        return name
    return short

def format_tag(ref, tag, repository):
    d = {}
    d['name'] = tag.name
    d['tag'] = tag.name
    d['target'] = tag.target.hex
    d['type'] = 'tag'
    d['tagger'] = format_pygit2_signature(tag.tagger)
    d['message'], _, d['body'] = tag.message.strip().partition('\n\n')
    d['sha'] = tag.hex
    return d

def format_lw_tag(ref, tag, repository):
    d = {}
    d['name'] = format_short_reference_name(ref)
    d['tag']  = d['name']
    d['object'] = tag.hex
    d['type'] = 'commit'
    d['commit'] = format_commit(ref, tag, repository)
    return d

def format_blob(sha, blob, repository):
    resp = Response(stream_with_context(blob.data))
    resp.headers['X-Accel-Buffering'] = 'no'
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Content-Length'] = len(blob.data)
    resp.headers['Content-Type'] = magic.from_buffer(blob.data, mime=True)
    return resp

def format_tree(sha, tree, repository):
    res = []
    for entry in tree:
        mode = '%06o' % entry.filemode
        # FIXME: use pygit2 object
        if mode == '160000':
            objtype = 'commit'  # For git submodules
        elif mode == '040000':
            objtype = 'tree'
        else:
            objtype = 'blob'
        r = {
            'sha': entry.hex,
            'mode': mode,
            'type': objtype,
            'path': entry.name
        }
        res.append(r)
    return res

def format_commit(sha, commit, repository):
    d = {}
    d['parent'] = [p.hex for p in commit.parents] if commit.parents else []
    d['tree'] = commit.tree.hex
    d['committer'] = format_pygit2_signature(commit.committer)
    d['author'] = format_pygit2_signature(commit.author)
    d['message'], _, d['body'] = commit.message.strip().partition('\n\n')
    d['sha'] = commit.hex
    return d

class GitRepository(Repository):

    def revparse_single(self, *w, **kw):
        try:
            return super(GitRepository, self).revparse_single(*w, **kw)
        except (KeyError, ValueError):
            raise JagareError("rev not found.", 400)

    def lookup_reference(self, *w, **kw):
        try:
            return super(GitRepository, self).lookup_reference(*w, **kw)
        except ValueError:
            raise JagareError("reference not found.", 400)

    def read(self, *w, **kw):
        try:
            return super(GitRepository, self).read(*w, **kw)
        except ValueError:
            raise JagareError("sha not found", 400)

