import logging
import socket
from slaveapi.clients.ssh import RemoteCommandError

from ..clients import slavealloc
from ..slave import Slave, get_console
from .reboot import reboot
from .shutdown_buildslave import shutdown_buildslave
from .results import SUCCESS, FAILURE
from ..global_state import config
from slaveapi.machines.base import Machine
from ..slaveapi.util import value_in_values

log = logging.getLogger(__name__)


def get_free_ip(console, aws_config, max_attempts=3):
    attempt = 1
    while attempt < max_attempts:
        free_ip_rc, free_ip_output = console.run_cmd(
            'python cloud-tools/scripts/free_ips.py -c %s -r us-east-1 -n1' %
            aws_config
        )
        if free_ip_output:
            # double-check that the IP address isn't in use by another machine
            try:
                # use socket to mimic unix 'host' cmd
                socket.gethostbyaddr(free_ip_output)
            except socket.herror:
                # no address found with that ip so we can assume it is free!
                return free_ip_output
        attempt += 1
    return None


def aws_create_instance(email, bug, instance_type, arch=64):
    """Attempts to create an aws instance for a given owner


    :param email: the full ldap username of owner requesting instance
    :type email: str
    :param bug: the number of the bug that needs the instance
    :type bug: str
    :param instance_type: accepted values are 'build' and 'test'
    :type instance_type: str

    :rtype: tuple
    """
    # web end point will verify these validations but we should still double
    # check in case this is called from another location, e.g. another action
    assert value_in_values(instance_type, ['build', 'test'])
    assert arch != 32 and instance_type == 'build'

    status_msgs = ["Creating aws instance for `%s`" % email]
    return_code = SUCCESS  # innocent until proven guilty!
    # strip out the nickname of the loanee from their email
    nick = email.split('@')[0]

    if instance_type == 'build':
        host = 'dev-linux64-ec2-%s' % nick
        fqdn = '%s.dev.releng.use1.mozilla.com' % host
        aws_config = 'cloud-tools/configs/dev-linux%s' % arch
    else:  # instance_type == 'test'
        host = 'tst-linux%s-ec2-%s' % (arch, nick)
        fqdn = '%s.test.releng.use1.mozilla.com' % host
        aws_config = 'cloud-tools/configs/tst-linux%s' % arch

    aws_manager = Machine('aws-manager1')
    console = get_console(aws_manager, usernames=['root'])
    try:
        # for now let's use root to get at buildduty
        # and set up env
        console.run_cmd('su - buildduty')
        console.run_cmd('cd /builds/aws_manager/cloud-tools/scripts')
        console.run_cmd('source /builds/aws_manager/bin/activate')

        log.debug("email: %s, bug: %s - generating free ip" % (email, bug))
        free_ip = get_free_ip(console, aws_config)
        if not free_ip:
            log.debug("email: %s, bug: %s - failed to generate a free ip for "
                      "creating an aws instance" % (email, bug))
            return FAILURE, "failed to generate a free ip for aws creation"
        log.debug('email: %s, bug: %s - creating dns entries against ip: %s, '
                  'and host: %s' % (email, bug, free_ip, host))

        # TODO START HERE TOMORROW

    except RemoteCommandError:
        return_code = FAILURE
    if return_code == FAILURE:
        pass

    return return_code, "\n".join(status_msgs)
