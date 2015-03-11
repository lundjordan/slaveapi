from collections import defaultdict
from furl import furl

import requests
from requests import RequestException

import logging
from ..global_state import config
from slaveapi.actions.results import SUCCESS, FAILURE

log = logging.getLogger(__name__)


def find_key_value(info, wanted_key):
    if not info["key_value"]:
        return None

    for key, value in [(i["key"],i["value"]) for i in info["key_value"]]:
        if key == wanted_key:
            return value
    else:
        return None


def _create_record(ip, payload, desc, _type):
    url = furl(config["inventory_api_url"])

    # remove un-needed removal once bug 1030332 is resolved
    url.path.remove(str(url.path))  # trims path if present

    # now add the path that we can update from
    url.path.add('en-US/mozdns/api/v1_dns/{0}'.format(_type))

    payload.update({
        "ip_str": ip,
        "description": desc,
        "ip_type": "4",
        "views": ["private"],
    })
    auth = (config["inventory_username"], config["inventory_password"])
    return_msg = "{0} - Post request to {1} with {2}..".format(ip, url, payload)

    try:
        response = requests.post(str(url), data=payload, auth=auth)
    except RequestException as e:
        return_msg += ("{0} - exception while creating {1} in "
                       "inventory: {2}".format(ip, _type, e))
        log.exception(return_msg)
        return FAILURE, return_msg

    if response.status_code == 200:
        return SUCCESS, return_msg
    else:
        return_msg = "Failed\n{0} - error response msg: {1}".format(
            response.status_code, response.reason
        )
        return FAILURE, return_msg


def create_address_record(ip, fqdn, desc):
    payload = {'fqdn': fqdn}
    return _create_record(ip, payload, desc, _type='addressrecord')


def create_ptr_record(ip, fqdn, desc):
    payload = {'name': fqdn}
    return _create_record(ip, payload, desc, _type='ptr')


def create_dns(ip, fqdn, desc):
    return_code, a_msg = create_address_record(ip, fqdn, desc)
    if return_code == SUCCESS:
        return_code, ptr_msg = create_ptr_record(ip, fqdn, desc)
    return return_code, "\n".join([a_msg, ptr_msg])


def get_system(fqdn):
    url = furl(config["inventory_api_url"])

    # remove condition when bug 1030332 is resolved. below supports api
    # without any path set
    if not str(url.path):
        url.path.add('/en-US/tasty/v3/')

    url.path.add("system")
    url.args["format"] = "json"
    url.args["hostname"] = fqdn
    auth = (config["inventory_username"], config["inventory_password"])
    log.debug("Making request to %s", url)
    info = defaultdict(lambda: None)
    try:
        result = requests.get(str(url), auth=auth).json()["objects"][0]
        info.update(result)
    except IndexError:
        pass # It's ok to have no valid host (e.g. ec2)

    # We do some post processing because PDUs are buried in the key/value store
    # for some hosts.
    pdu = find_key_value(info, "system.pdu.0")
    if pdu:
        pdu, pdu_port = pdu.split(":")
        if not pdu.endswith(".mozilla.com"):
            pdu += ".mozilla.com"
        info["pdu_fqdn"] = pdu
        info["pdu_port"] = pdu_port

    # If the system has a mozpool server managing it, it's expressed as this key
    imaging_server = find_key_value(info, "system.imaging_server.0")
    if imaging_server:
        info["imaging_server"] = imaging_server
    return info
