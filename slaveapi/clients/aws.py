import logging
import os
import socket
import subprocess

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
        ip = subprocess.check_output(
            'python {free_ip} -c {config} -r {region} -n1'.format(
                free_ip=free_ip_script, config=config_path, region=region
            )
        )
        if ip_is_valid(ip):
            if ip_is_free(ip):
                return ip
        attempt += 1
    return None


def create_aws_instance(host, email, bug, aws_config, data, region='use-east-1'):
    create_script = os.path.join(config['cloud_tools_path'],
                                 'scripts/aws_create_instance.py')
    config_path = os.path.join(config['cloud_tools_path'],
                               'configs', aws_config)
    data_path = os.path.join(config['cloud_tools_path'], 'instance_data',
                             data)
    output = subprocess.check_output(
        'python {create_script} -c {config} -r {region} -s aws-releng'
        '--ssh-key {ssh_key} -k {aws_secrets} --loaned-to {email} --bug {bug}'
        '-i {instance_data} {host}'.format(
            create_script=create_script, config=config_path, region=region,
            ssh_key=config['aws_ssh_key'], aws_secrets=config['aws_secrets'],
            email=email, bug=bug, instance_data=data_path, host=host
        )
    )
    # TODO - NOW PARSE OUTPUT RETURN RESULT


# TODO add the following functions
# def terminate_aws_instance(name):
#     if is_ec2_instance(name):
#         result_code, result_msg = do_action(name)
#         return result_code, result_msg
#     else:
#         return FAILURE, "%s - slave not found in aws".format(name)
#
# def start_aws_instance(slave):
#     pass
#
# def stop_aws_instance(slave):
#     pass
#
# def query_aws_instance(slave):
#     pass

