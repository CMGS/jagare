#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  14:45:07 28/06/2013
# MODIFIED: 16:40:39 01/07/2013

from __future__ import absolute_import

from flask import json
from flask import make_response

def make_message_response(message, **kwargs):
    response_dict = {
        "message" : message,
        "error"   : 0,
    }
    response_dict.update(kwargs)
    return make_response(json.jsonify(response_dict), 200)

