#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:34:16 03/06/2013
# MODIFIED: 15:25:23 03/07/2013

import gevent
import urlparse
from StringIO import StringIO
from ConfigParser import RawConfigParser # NOTICE: this module changed name to `configparser` in python 3.x

from flask import request
from flask import Blueprint
from flask.views import MethodView

from pygit2 import GIT_OBJ_TAG
from pygit2 import GIT_OBJ_BLOB
from pygit2 import GIT_OBJ_TREE
from pygit2 import GIT_OBJ_COMMIT
from pygit2 import GIT_SORT_TOPOLOGICAL

from jagare.error import JagareError
from jagare.utils.git import format_commit
from jagare.utils.decorators import jsonize
from jagare.utils.decorators import require_project_name

TREE_ORDER = {
    'tree'      : 1, \
    'submodule' : 2, \
    'blob'      : 3, \
}

class LsTree(object):

    def _walk_tree(self, tree, path=None):
        _list = []
        for entry in tree:
            _list.append((entry, path))
        return _list

    def _remove_slash(self, path):
        if path[-1] == '/':
            return path[:-1]
        return path

    def _format_submodule_conf(self, raw):
        if isinstance(raw, unicode):
            lines = raw.splitlines()
        elif isinstance(raw, str):
            lines = raw.decode("UTF-8").splitlines()
        else:
            return None

        lines = map(lambda line: line.strip(), lines)
        return "\n".join(lines)

    def _read_blob(self, repository, sha):
        obj = repository.revparse_single(sha)

        if obj.type != GIT_OBJ_BLOB:
            return None
        return obj.data

    def _parse_submodule(self, repository, submodule_obj):
        # get ref
        submodule_conf_raw = self._read_blob(repository, submodule_obj.hex)
        submodule_conf_raw = self._format_submodule_conf(submodule_conf_raw)

        config = RawConfigParser(allow_no_value = True)
        config.readfp(StringIO(submodule_conf_raw))

        return config

    def _parse_submodule_url(self, url):
        parser = urlparse.urlparse(url)
        netloc = parser.netloc

        if not netloc:
            # for scp-like url, e.g. git@github.com:xxxx/xxx.git
            if parser.path == url:
                netloc = parser.path.split(':')[0].split('@')[-1]
            else:
                return url

        elif netloc == 'code.dapps.douban.com':
            return 'code'
        elif netloc == 'github.com':
            return 'github'
        elif netloc == 'github-ent.intra.douban.com':
            return 'github-ent'
        return netloc

    def _calc_is_changed(self, commit, path, ret):
        if commit.is_changed([path], no_diff=True)[0]:
            ret[path] = 1

    def _format_with_last_commit(self, repository, ret_tree, to_commit):
        walker = repository.walk(to_commit.oid, GIT_SORT_TOPOLOGICAL)
        paths = [k for k, v in ret_tree.iteritems()]
        ret = {}

        for commit in walker:
            spawns = [gevent.spawn(self._calc_is_changed, commit, path, ret) for path in paths]
            gevent.joinall(spawns)
            if not ret:
                continue
            fc = format_commit(commit.hex, commit, None)
            for path, r in ret.iteritems():
                ret_tree[path]['commit'] = fc
                paths.remove(path)
            if not paths:
                break
            ret = {}

    def get_tree_list(self, repository, exists, ref, \
                      recursive = None, size = None, name_only = None, \
                      req_path = None, with_commit = False):
        if req_path:
            req_path = self._remove_slash(req_path)

        try:
            obj = repository.revparse_single(ref)
        except (ValueError, KeyError):
            raise JagareError("Reference not found.", 404)

        commit_obj = None

        if obj.type == GIT_OBJ_TREE:
            tree_obj = obj
        elif obj.type == GIT_OBJ_TAG:
            commit_obj = repository.revparse_single(obj.target.hex)
            tree_obj = commit_obj.tree
        elif obj.type == GIT_OBJ_BLOB:
            raise JagareError("Object is blob, doesn't contain any tree", 400)
        elif obj.type == GIT_OBJ_COMMIT:
            commit_obj = obj
            tree_obj = obj.tree

        walker = self._walk_tree(tree_obj)

        ret_tree = {}
        submodule_obj = None

        for index, (entry, path) in enumerate(walker):
            mode = '%06o' % entry.filemode
            if mode == '160000':
                objtype = 'submodule'  # For git submodules
            elif mode == '040000':
                objtype = 'tree'
            else:
                objtype = 'blob'
            path = "%s/%s" % (path, entry.name) if path else entry.name

            if path == '.gitmodules':
                submodule_obj = entry

            if recursive or (req_path and req_path.startswith(path)):
                if objtype == 'tree':
                    _tree = repository[entry.oid]
                    _tree_list = self._walk_tree(_tree, path)
                    for _index, _entry in enumerate(_tree_list):
                        if recursive:
                            walker.insert(index + _index + 1, _entry)
                        elif req_path and req_path.startswith(_entry[-1]):
                            walker.insert(index + _index + 1, _entry)
                    continue

            if req_path:
                if not path.startswith(req_path):
                    continue

            if name_only:
                ret_tree['path'] = path
                continue

            item = {
                "mode" : mode, \
                "type" : objtype, \
                "sha"  : entry.hex, \
                "path" : path, \
                "name" : entry.name
            }

            if item['type'] == 'submodule':
                submodule = self._parse_submodule(repository, submodule_obj)
                section_name = 'submodule "{submodule_name}"'.format(submodule_name = path)

                if submodule.has_section(section_name):
                    item['submodule'] = dict(submodule.items(section_name))
                    item['submodule']['host'] = self._parse_submodule_url(item['submodule']['url'])

                    if item['submodule']['url'].endswith('.git'):
                        item['submodule']['url'] = item['submodule']['url'][:-4]

            if size:
                if objtype == 'blob':
                    blob = repository[entry.oid]
                    item['size'] = blob.size
                else:
                    item['size'] = '-'

            ret_tree[path] = item

        if name_only:
            return ret_tree.values()

        if with_commit and commit_obj:
            self._format_with_last_commit(repository, ret_tree, commit_obj)

        tree_list = ret_tree.values()
        tree_list.sort(key=lambda i: (TREE_ORDER[i['type']], i['name']))
        return tree_list

class LsTreeView(MethodView):

    decorators = [require_project_name("name"), jsonize]

    def get(self, repository, exists, ref):
        from jagare.views.cat import Cat

        recursive = request.args.get("recursive", None)
        size = request.args.get("size", None)
        name_only = request.args.get("name_only", None)
        req_path = request.args.get("path", None)
        with_commit = request.args.get("with_commit", False)

        ls_tree = LsTree()
        content = ls_tree.get_tree_list(repository, exists, ref, recursive, size, name_only, req_path, with_commit)
        cat = Cat()
        meta = cat.cat_by_ref(repository, ref)
        return {'meta':meta, 'content':content}

ls_tree_view = LsTreeView.as_view('ls_tree')

bp = Blueprint('ls_tree', __name__)
bp.add_url_rule('/<path:ref>', view_func = ls_tree_view, methods = ["GET"])

