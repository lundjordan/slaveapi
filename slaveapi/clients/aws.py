import logging
import os
import socket
from subprocess import check_output, check_call, CalledProcessError, Popen
from slaveapi.actions.results import FAILURE, SUCCESS

log = logging.getLogger(__name__)
from ..global_state import config


def ip_is_valid(address):
    try:
        socket.inet_aton(address)
        ip = True
    except socket.error:
        ip = False

    log.debug("{ip} -- free_ips.py generated a non valid ip".format(address))
    return ip


def ip_is_free(address):
    # TODO - we should use inventory to validate an address being free or not
    try:
        socket.gethostbyaddr(address)
        free = False
    except socket.herror:
        # no address found with that ip so we can assume it is free!
        free = True
    log.debug("{ip} - free_ips.py generated a non free ip".format(address))
    return free


def get_free_ip(aws_config, region='us-east-1', max_attempts=3):
    free_ip_script = os.path.join(config['cloud_tools_path'],
                                  'scripts/free_ips.py')
    config_path = os.path.join(config['cloud_tools_path'],
                               'configs', aws_config)
    attempt = 1
    while attempt < max_attempts:
        ip = check_output(
            'python {free_ip} -c {config} -r {region} -n1'.format(
                free_ip=free_ip_script, config=config_path, region=region
            )
        )
        if ip_is_valid(ip):
            if ip_is_free(ip):
                return ip
        attempt += 1
    return None


def create_aws_instance(fqdn, host, email, bug, aws_config, data,
                        region='use-east-1'):
    create_script = os.path.join(config['cloud_tools_path'],
                                 'scripts/aws_create_instance.py')
    config_path = os.path.join(config['cloud_tools_path'],
                               'configs', aws_config)
    data_path = os.path.join(config['cloud_tools_path'], 'instance_data',
                             data)
    try:
        check_call(
            ['python', create_script, '-c', config_path, '-r', region, '-s',
             'aws-releng', '--ssh-key', config['aws_ssh_key'], '-k',
             config['aws_secrets'], '--loaned-to', email, '--bug', bug,
             '-i', data_path, fqdn], cwd=config['aws_base_path'],
        )
    except CalledProcessError as e:
        fail_msg = "{0} - failed to create instance. error: {1}".format(host, e)
        log.warning(fail_msg)
        return FAILURE, fail_msg

    # return code of check_call was good, let's poke the status of this instance
    tags = query_aws_instance(host)

    # aws_create_instance.py adds certain tags for validation.
    # e.g. if 'moz-state' == 'ready' we puppetized properly
    validated = all([
        tags.get('FQDN') == fqdn,
        tags.get('moz-loaned-to') == email,
        tags.get('moz-state') == 'ready',
        tags.get('created')
    ])
    if validated:
        return SUCCESS, str(tags)  # return instance information

    fail_msg = ("{0} - Instance could not be confirmed created or puppetized. "
                "Tags known: {1}".format(host, tags or "None"))
    log.warning(fail_msg)
    return FAILURE, fail_msg


def query_aws_instance(name):
    query_script = os.path.join(config['cloud_tools_path'],
                                'scripts/aws_manage_instances.py')
    output = check_output(['python', query_script, 'status', name])

    if output:  # instance exists
        # parse the output for all the tags
        tags = output.split('Tags:', 1)[1].split('\n', 1)[0].split(',')
        # make a dict out of the tags and return that
        return dict(tag.replace(" ", "").split('->') for tag in tags)
    return {}
