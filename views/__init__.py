#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  15:32:59 23/05/2013
# MODIFIED: 17:51:49 21/06/2013

'''
Views
~~~~~
'''

from views import mixes

def init_view(app):
    app.register_blueprint(mixes.bp, url_prefix = '/<path:name>')
