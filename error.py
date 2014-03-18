#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  11:09:24 28/06/2013
# MODIFIED: 11:18:26 28/06/2013

from flask import json
from flask import make_response

class JagareError(Exception):

    def __init__(self, message, status_code):

        assert isinstance(message, basestring), TypeError("Error Message must be a string.")
        assert isinstance(status_code, int), TypeError("HTTP Status Code must be an integer.")

        self.message = message
        self.status_code = status_code

    def __repr__(self):
        return "<JagareError {message} HTTP {status_code}>".format(message = self.message, 
                                                                   status_code = self.status_code)
    def make_response(self):
        json_retval = json.jsonify({"message" : self.message, "error" : 1})
        return make_response(json_retval, self.status_code)

