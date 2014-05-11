from .results import SUCCESS, FAILURE

from flask import request

from ..clients.slavealloc import update_slavealloc

import logging
log = logging.getLogger(__name__)

def normalize_truthiness(val):
    if val == "n" or val == "no":
        return 0
    if val == "disabled" or val == False:
        return 0
    if val == 0:
        return 0
    if val == "y" or val == "yes":
        return 1
    if val == "enabled" or val == True:
        return 1
    if val == 1:
        return 1
    raise ValueError("Unsupported value (%s) for truthiness" % val)

def update(name):
    args = request.args
    
    slavealloc_values={}
    for key, value in args.items():
        if key == "enabled":
            # Normalize value
            slavealloc_values['enabled'] = normalize_truthiness(value)
        else:
            raise ValueError("Unsupported update arg %s" % key)
    if update_slavealloc(**slavealloc_values):
        return SUCCESS, "Successfully updated slavealloc (%s)" % repr(args)
    return FAILURE, "Missing features to update."