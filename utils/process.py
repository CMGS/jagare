#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR:   fanzeyi
# CREATED:  10:40:56 24/06/2013
# MODIFIED: 15:26:02 24/06/2013

import shlex
import logging
import subprocess

from config import GIT_EXECUTABLE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _shlex_split(cmd):
    if isinstance(cmd, unicode):
        return [c.decode("utf-8") for c in shlex.split(cmd.encode("utf-8"))]
    elif isinstance(cmd, str):
        return shlex.split(cmd.encode("utf-8"))
    elif not isinstance(cmd, list):
        return list(cmd)
    return cmd

def _call(cmd):
    try:
        process = subprocess.Popen(cmd, stdout = subprocess.PIPE, \
                                   stderr = subprocess.PIPE)
    except (OSError, TypeError) as err:
        logger.error("Error occurrred when calling %s" % " ".join(cmd))
        raise err
    out, err = process.communicate()
    out = str(out)
    err = str(err)

    result = {}

    result['returncode'] = process.returncode
    result['stdout'] = out
    result['stderr'] = err 
    result['fullcmd'] = " ".join(cmd)
    return result

def call(repository, cmd):
    cmd = _shlex_split(cmd)
    add2cmd = ['--git-dir', repository.path]
    return _call([GIT_EXECUTABLE] + add2cmd + cmd)
