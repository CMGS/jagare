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

from views import init
from views import mixes
from views import clone

def init_view(app):
    app.register_blueprint(init.bp, url_prefix = '/<path:name>/init')
    app.register_blueprint(mixes.bp, url_prefix = '/<path:name>')
    app.register_blueprint(clone.bp, url_prefix = '/<path:name>/clone')
