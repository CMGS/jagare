#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  11:15:30 18/06/2013
# MODIFIED: 13:47:35 02/07/2013

import os
import shutil
import config

from flask import request
from flask import Blueprint
from flask import make_response

from error import JagareError

from ellen.repo import Jagare

from utils.git import endwith_git
from utils.git import is_repository
from utils.flask import make_message_response
from utils.decorators import jsonize
from utils.decorators import require_repository

bp = Blueprint('mixes', __name__)

@bp.route('')
@bp.route('/info')
@jsonize
@require_repository
def info(repository):
    retdict = {}
    retdict["path"]  = repository.path
    retdict["empty"] = repository.empty
    retdict["bare"]  = repository.bare
    retdict["head"]  = str(repository.head.target) if repository.head else None
    return retdict

@bp.route('/init', methods = ["POST"])
def init(name):
    repository_path = os.path.join(config.REPOS_PATH, name)
    repository_path = endwith_git(repository_path)
    
    repository_exist = is_repository(repository_path)
    
    if repository_exist:
        raise JagareError("repository already exists.", 409)
    
    Jagare.init(repository_path)
    
    return make_message_response("initialize success")

@bp.route('/delete', methods = ["POST"])
@require_repository
def delete(repository):
    shutil.rmtree(repository.path)
    return make_message_response("delete success")

@bp.route('/clone/<path:clone_from>', methods = ["POST"])
def clone(name, clone_from):
    target_path = os.path.join(config.REPOS_PATH, name)
    target_path = endwith_git(target_path)
    
    clone_path = os.path.join(config.REPOS_PATH, clone_from)
    clone_path = endwith_git(clone_path)
    
    repository_exist = is_repository(target_path)
    
    if repository_exist:
        raise JagareError("repository already exists", 409)
    
    clone_repository_exist = is_repository(clone_path)
    
    if not clone_repository_exist:
        raise JagareError("clone repository does not exist", 400)

    jagare = Jagare(clone_path)
    jagare.clone(target_path, bare=True)
    
    return make_message_response("clone success")

@bp.route('/mirror/<path:url>', methods = ["POST"])
def mirror(name, url):
    target_path = os.path.join(config.REPOS_PATH, name)
    target_path = endwith_git(target_path)

    repository_exist = is_repository(target_path)
    
    if repository_exist:
        raise JagareError("repository already exists", 409)

    Jagare.mirror(url, target_path)
    
    return make_message_response("Mirror success.")


@bp.route('/branches')
@jsonize
@require_repository
def branches(repository):
    return repository.branches

@bp.route('/tags')
@jsonize
@require_repository
def tags(repository):
    return repository.tags

@bp.route('/ls-tree/<path:ref>')
@jsonize
@require_repository
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
@require_repository
def blame(repository, ref):
    path = request.args.get('path', None)
    lineno = request.args.get('lineno', None, type = int)
    return repository.blame(ref, path, lineno)

@bp.route('/format-patch/<path:from_ref>')
@bp.route('/format-patch/<path:from_ref>/to/<path:to_ref>')
@jsonize
@require_repository
def format_patch(repository, from_ref, to_ref = 'HEAD'):
    return repository.format_patch(to_ref, from_ref)

@bp.route('/sha/<path:rev>')
@jsonize
@require_repository
def sha(repository, rev):
    return repository.sha(rev)

@bp.route('/update-hooks/<path:path>', methods = ['POST'])
@jsonize
@require_repository
def update_hooks(repository, path):
    repository.update_hooks(path)
    return make_message_response("success to update hooks")

@bp.route('/show/<path:ref>')
@jsonize
@require_repository
def show(repository, ref):
    return repository.show(ref)

@bp.route('/rev-list/<path:to_ref>')
@bp.route('/rev-list/<path:to_ref>/from/<path:from_ref>')
@jsonize
@require_repository
def rev_list(repository, to_ref, from_ref = None):
    path = request.args.get('path', None)
    skip = request.args.get('skip', 0, type = int)
    max_count = request.args.get('max_count', 0, type = int)
    author = request.args.get('author', None)
    query = request.args.get('query', None)
    first_parent = request.args.get('first_parent', None)
    since = request.args.get('since', 0, type = int)
    no_merges = request.args.get('no_merges', None)
    return repository.rev_list(to_ref, from_ref = from_ref, path = path, skip = skip, max_count = max_count, author = author, query = query, first_parent = first_parent, since = since, no_merges = no_merges)

@bp.route('/commit', methods = ['POST'])
@jsonize
@require_repository
def create_commit(repository):
    branch = request.form['branch']
    parent = request.form['parent']
    author_name = request.form['author_name']
    author_email = request.form['author_email']
    message = request.form['message']
    reflog = request.form['reflog']
    #TODO
    # return repository.commit_file()

@bp.route('/diff/<path:to_ref>')
@bp.route('/diff/<path:to_ref>/from/<path:from_ref>')
@jsonize
@require_repository
def diff(repository, to_ref, from_ref = None):
    diff = repository.diff(to_ref, from_ref)
    diff['diff'] = diff['diff'].patch
    return diff

@bp.route('/resolve-commit/<path:version>')
@jsonize
@require_repository
def resolve_commit(repository, version):
    return repository.resolve_commit(version)

@bp.route('/resolve-type/<path:version>')
@jsonize
@require_repository
def resolve_type(repository, version):
    return repository.resolve_type(version)

@bp.route('/branch/<path:branchName>/create', methods = ['POST'])
@jsonize
@require_repository
def create_branch(repository, branchName):
    ref = request.form['ref']
    force = bool(request.form.get('force', 0, type = int))
    if repository.create_branch(branchName, ref, force):
        return make_message_response("Branch create success.")
    else:
        raise JagareError("Branch create failed.")

@bp.route('/branch/<path:branchName>/delete', methods = ['POST'])
@jsonize
@require_repository
def delete_branch(repository, branchName):
    repository.delete_branch(branchName)
    return make_message_response("Branch delete success")

@bp.route('/tag/<path:tagName>/create', methods = ['POST'])
@jsonize
@require_repository
def create_tag(repository, tagName):
    ref = request.form['ref']
    author_name = request.form['author_name']
    author_email = request.form['author_email']
    message = request.form['message']
    return repository.create_tag(tagName, ref = ref, author_name = author_name, author_email = author_email, message = message)

@bp.route('/archive')
@bp.route('/archive/<path:ref>')
@require_repository
def archive(repository, ref = 'HEAD'):
    binary = repository.archive(prefix = '', ref = ref)
    resp = make_response(binary)
    resp.headers['content-type'] = 'application/x-tar; charset=binary'
    return resp

@bp.route('/push/<path:remote>/ref/<path:ref>', methods = ['POST'])
@jsonize
@require_repository
def push(repository, remote, ref):
    enviorn = request.form.to_dict()
    return repository.push(remote, ref, enviorn)

@bp.route('/merge/<path:ref>', methods = ['POST'])
@jsonize
@require_repository
def merge(repository, ref):
    msg = request.form.get('msg', 'automerge')
    commit_msg = request.form.get('commit_msg', '')
    no_ff = bool(request.form.get('no_ff', 0))
    return repository.merge(ref, msg = msg, commit_msg = commit_msg, no_ff = no_ff)

@bp.route('/merge-tree/<path:ours>/with/<path:theirs>', methods = ['POST'])
@jsonize
@require_repository
def merge_tree(repository, ours, theirs):
    return repository.merge_tree(ours, theirs)

@bp.route('/merge-head/<path:ref>', methods = ['POST'])
@jsonize
@require_repository
def merge_head(repository, ref):
    return repository.merge_head(ref)

@bp.route('/merge-commits/<path:ours>/with/<path:theirs>', methods = ['POST'])
@jsonize
@require_repository
def merge_commits(repository, ours, theirs):
    return repository.merge_commits(ours, theirs)

@bp.route('/merge-base/<path:from_sha>/to/<path:to_sha>', methods = ["POST"])
@require_repository
def merge_base(repository, from_sha, to_sha):
    repository.merge_base(to_sha, from_sha)
    return make_message_response("Merged.")

@bp.route('/remotes')
@jsonize
@require_repository
def remotes(repository):
    if callable(repository.remotes):
        _remotes = repository.remotes()
        return [dict(name = remote.name, url = remote.url) for remote in _remotes]
    return repository.remotes

@bp.route('/remote/<path:name>/fetch', methods = ["POST"])
@require_repository
def fetch(repository, name):
    repository.fetch(name)
    return make_message_response("Remote fetched successfully.")

@bp.route('/remote/fetch-all', methods = ["POST"])
@require_repository
def fetch_all(repository):
    repository.fetch_all()
    return make_message_response("All remotes fetched.")

@bp.route('/remote/<path:name>/create', methods = ["POST"])
@require_repository
def add_remote(repository, name):
    url = request.form['url']
    repository.add_remote(name, url)
    return make_message_response("Remote created.")

@bp.route('/detect-renamed/<path:ref>', methods = ["POST"])
@jsonize
@require_repository
def detect_renamed(repository, ref):
    return repository.detect_renamed(ref)
