from furl import furl

import requests
import json

import logging
log = logging.getLogger(__name__)

def get_slave(api, id_=None, name=None):
    if id_ and name:
        raise ValueError("Can't retrieve slave by id and name at the same time.")

    url = furl(api)
    if id_:
        url.path.add("slaves/%s" % id_)
    elif name:
        url.path.add("slaves/%s" % name)
        url.args["byname"] = 1
    else:
        raise Exception()

    log.info("Making request to: %s", url)
    return requests.get(str(url)).json()

def get_slave_id(api, name):
    return get_slave(api, name=name)['slaveid']

def update_slavealloc(api, id_=None, name=None, data={}):
    if id_ and name:
        raise ValueError("Can't update slave by id and name at the same time.")
    
    if not data:
        raise ValueError("Missing data to update")

    id = id_
    if not id_:
        id = get_slave_id(api, name=name)
    url = furl(api)
    url.path.add("slaves/%s" % id)
    data_ = json.dumps(data)
    res = results.put(str(url), data=data_).json()
    if 'status' in res and res['success']:
        return True
    return False

def get_slaves(api, purposes=[], environs=[], pools=[], enabled=None):
    url = furl(api)
    url.path.add("slaves")
    url.args["purpose"] = purposes
    url.args["environment"] = environs
    url.args["pool"] = pools
    if enabled:
        url.args["enabled"] = int(enabled)

    log.info("Making request to: %s", url)
    return requests.get(str(url)).json()


def get_master(api, id_):
    url = furl(api)
    url.path.add("masters/%s" % id_)
    return requests.get(str(url)).json()
