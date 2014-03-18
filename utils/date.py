#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  15:45:30 13/06/2013
# MODIFIED: 16:01:16 13/06/2013
'''
date
----

.. autoclass:: FixedOffset

'''

from datetime import tzinfo
from datetime import timedelta

ZERO = timedelta(0)

class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO
