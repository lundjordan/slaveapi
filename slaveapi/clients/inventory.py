from collections import defaultdict
from furl import furl

import requests

import logging
log = logging.getLogger(__name__)

def find_key_value(info, wanted_key):
    if not info["key_value"]:
        return None

    for key, value in [(i["key"],i["value"]) for i in info["key_value"]]:
        if key == wanted_key:
            return value
    else:
        return None


def _create_record(ip, api, fqdn, desc, username, password, _type):
    url = furl(api)

    # remove un-needed removal once bug 1030332 is resolved
    url.path.remove(str(url.path))  # trims path if present

    # now add the path that we can update from
    url.path.add('en-US/mozdns/api/v1_dns/')
    if _type == 'a':
        url.path.add('addressrecord')
        fqdn_title = 'fqdn'
    elif _type == 'ptr':
        url.path.add('ptr')
        fqdn_title = 'name'
    else:
        raise ValueError("only 'a' and 'ptr' are valid for _type. Got %s" % _type)
    payload = {
        "ip_str": ip,
        "description": desc,
        fqdn_title: fqdn,
        "ip_type": "4",
        "views": ["private"],
    }
    auth = (username, password)
    log.debug("%s - Post request to %s with payload %s", fqdn, url, payload)

    return requests.post(str(url), data=payload, auth=auth)


def create_address_record(ip, api, fqdn, desc, username, password):
    result = _create_record(ip, api, fqdn, desc, username, password, _type='a')


def create_ptr_record(ip, api, fqdn, desc, username, password):
    result = _create_record(ip, api, fqdn, desc, username, password, _type='ptr')


def get_system(fqdn, api, username, password):
    url = furl(api)

    # remove condition when bug 1030332 is resolved. below supports api
    # without any path set
    if not str(url.path):
        url.path.add('/en-US/tasty/v3/')

    url.path.add("system")
    url.args["format"] = "json"
    url.args["hostname"] = fqdn
    auth = (username, password)
    log.debug("%s - Making request to %s", fqdn, url)
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
