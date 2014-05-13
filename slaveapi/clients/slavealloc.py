from furl import furl

import requests
from requests import RequestException
import json

import logging
from slaveapi.actions.results import FAILURE, SUCCESS

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

def update_slave(api, name, values_to_update):
    """
    updates a slave's values in slavealloc.

    args:
        api (string) -- the root url for slaveallocs api
        name (string) -- the hostname of the slave being updated
        values_to_update (dict) -- the slave's values we wish to change

    returns:
        a tuple that consists of the return_code and return_msg
    """

    # http://slavealloc.build.mozilla.org/api/
    # dev-linux64-ec2-jlund2
    # http://slavealloc.build.mozilla.org/api/slaves/dev-linux64-ec2-jlund2?byname=1

    return_msg = "Updating slave %s in slavealloc..." % name

    url = furl(api)
    url.path.add("slaves")
    url.path.add("%s" % name)
    url.args['byname'] = 1
    values_jsonfied = json.dumps(values_to_update)

    try:
        response = requests.put(str(url), data=values_jsonfied)
    except RequestException as e:
        log.exception("%s - Caught exception while updating slavealloc.", name)
        log.exception("Exception message: %s" % e)
        return_msg += "Failed\nCaught exception while updating: %s" % (e,)
        return FAILURE, return_msg

    if response.status_code == response.codes.ok:
        return_msg += "Success"
        return_code = SUCCESS
    else:
        return_msg += "Failed\n"
        return_msg += 'response code while updating: %s' % response.status_code
        return_code = FAILURE

    return return_code, return_msg

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
