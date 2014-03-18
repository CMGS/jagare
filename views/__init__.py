#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  15:32:59 23/05/2013
# MODIFIED: 17:51:49 21/06/2013

'''
Views
~~~~~

.. automodule:: views.cat

.. automodule:: views.log

.. automodule:: views.init

.. automodule:: views.clone

.. automodule:: views.update_ref
'''

#from views import cat
#from views import log
from views import init
#from views import diff
#from views import mixes
#from views import clone
#from views import config
#from views import ls_tree
#from views import rev_list
#from views import update_ref
#from views import update_file

def init_view(app):
    #app.register_blueprint(cat.bp, url_prefix = '/<path:name>/cat') # mew.. 
    #app.register_blueprint(log.bp, url_prefix = '/<path:name>/log') # may be this should be a dog ?
    app.register_blueprint(init.bp, url_prefix = '/<path:name>/init')
    #app.register_blueprint(diff.bp, url_prefix = '/<path:name>/diff')
    #app.register_blueprint(mixes.bp, url_prefix = '/<path:name>')
    #app.register_blueprint(clone.bp, url_prefix = '/<path:name>/clone')
    #app.register_blueprint(config.bp, url_prefix = '/<path:name>/config')
    #app.register_blueprint(ls_tree.bp, url_prefix = '/<path:name>/ls-tree')
    #app.register_blueprint(rev_list.bp, url_prefix = '/<path:name>/rev-list')
    #app.register_blueprint(update_ref.bp, url_prefix = '/<path:name>/update-ref')
    #app.register_blueprint(update_file.bp, url_prefix = '/<path:name>/update-file')

