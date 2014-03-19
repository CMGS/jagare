#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  11:15:30 18/06/2013
# MODIFIED: 13:47:35 02/07/2013

from flask import request
from flask import Blueprint

from utils.flask import make_message_response
from utils.decorators import jsonize
from utils.decorators import require_repository

bp = Blueprint('mixes', __name__)

#@bp.route('', methods = ['GET'])
#@jsonize
#@require_project_name("name", require_not_empty = False)
#def repo_information(repository, exists):
#    return {"is_bare" : repository.is_bare, "is_empty" : repository.is_empty}
#
#@bp.route('/fetch_all', methods = ['POST'])
#@jsonize
#@require_project_name("name")
#def fetch_all(repository, exists):
#    # timeout ?
#    for remote in repository.remotes:
#        try:
#            remote.fetch()
#        except GitError:
#            pass
#    return make_message_response("fetch success")
#
#@bp.route('/add_remote/<path:remote_name>', methods = ['POST'])
#@jsonize
#@require_project_name("name")
#def add_remote(repository, exists, remote_name):
#    url = request.form.get('url', None)
#    if not url:
#        raise JagareError("url is required.", 400)
#    repository.create_remote(remote_name, url)
#    return make_message_response("add remote success")
#
#@bp.route('/list/tags', methods = ['GET'])
#@jsonize
#@require_project_name("name")
#def list_tags(repository, exists):
#    tags = []
#    refs = repository.listall_references()
#
#    for ref in refs:
#        if ref.startswith("refs/tags/"):
#            # this is a tag but maybe a lightweight tag
#            tag_obj = repository.revparse_single(ref)
#            if isinstance(tag_obj, Commit):
#                # lightweight tag
#                tags.append(format_lw_tag(ref, tag_obj, repository))
#            else:
#                tags.append(format_tag(ref, tag_obj, repository))
#
#    return tags
#
#@bp.route('/list/branches', methods = ['GET'])
#@jsonize
#@require_project_name("name")
#def list_branches(repository, exists):
#    branches = []
#    refs = repository.listall_references()
#
#    for ref in refs:
#        if ref.startswith("refs/heads/"):
#            branch = {}
#            commit_obj = repository.revparse_single(ref)
#            branch['name'] = format_short_reference_name(ref)
#            branch['commit'] = format_commit(ref, commit_obj, repository)
#            branches.append(branch)
#
#    return branches
#
#@bp.route('/blame/<path:ref>', methods = ['GET'])
#@jsonize
#@require_project_name("name")
#def blame(repository, exists, ref):
#    path = request.args["path"]
#    lineno = request.args.get("lineno", None)
#    
#    if lineno:
#        result = call(repository, 'blame -L %s,%s --porcelain %s -- %s' % (lineno, lineno, ref, path))
#    else:
#        result = call(repository, 'blame -p -CM %s -- %s' % (ref, path))
#    return result
#
#@bp.route('/update-hook', methods = ['POST'])
#@jsonize
#@require_project_name("name")
#def update_hook(repository, exists):
#    link = request.form.get("link", False)
#
#    hook_dir = os.path.join(repository.path, 'hooks')
#
#    # remove hook_dir
#    if os.path.exists(hook_dir):
#        if os.path.islink(hook_dir):
#            os.remove(hook_dir)
#        else:
#            shutil.rmtree(hook_dir)
#    
#    if link:
#        try:
#            os.symlink('/var/dae/apps/code/hub/hooks', hook_dir)
#        except OSError:
#            raise JagareError("Update hook failed.", 500)
#    return make_message_response("update hook success")

@bp.route('/branches')
@jsonize
@require_repository()
def branches(repository):
    return repository.branches

@bp.route('/tags')
@jsonize
@require_repository()
def tags(repository):
    return repository.tags

@bp.route('/ls-tree/<path:ref>')
@jsonize
@require_repository()
def ls_tree(repository, ref):
    # Can't use now, bug in upstream
    path = request.args.get('path', None)
    recursive = request.args.get('recursive', 0, type = int) == 1
    size = request.args.get('size', None)
    with_commit = request.args.get('with_commit', 0, type = int) == 1
    name_only = request.args.get('name_only', None)
    return repository.ls_tree(ref, path, recursive = recursive, size = size, with_commit = with_commit, name_only = name_only)

@bp.route('/blame/<path:ref>')
@jsonize
@require_repository()
def rev_list(repository, ref):
    path = request.args.get('path', None)
    lineno = request.args.get('lineno', None, type = int)
    return repository.blame(ref, path, lineno)

@bp.route('/format-patch/<path:from_ref>/to/<path:to_ref>')
@jsonize
@require_repository()
def format_patch(repository, from_ref, to_ref):
    return repository.format_patch(to_ref, from_ref)

@bp.route('/sha/<path:rev>')
@jsonize
@require_repository()
def sha(repository, rev):
    return repository.sha(rev)

@bp.route('/update-hooks/<path:path>', methods = ['POST'])
@jsonize
@require_repository()
def update_hooks(repository, path):
    repository.update_hooks(path)
    return make_message_response("success to update hooks")
