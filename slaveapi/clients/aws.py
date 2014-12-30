import logging
import os
from subprocess import check_output
from slaveapi.actions.results import SUCCESS

log = logging.getLogger(__name__)
from ..global_state import config


def _manage_instance(name, action, dry_run=False, force=False):
    query_script = os.path.join(config['cloud_tools_path'],
                                'scripts/aws_manage_instances.py')
    options = []
    if dry_run:
        options.append('--dry-run')
    if force:
        options.append('--force')

    return check_output(['python', query_script] + options + [action, name])


def terminate_instance(name):
    output = _manage_instance(name, 'terminate', dry_run=True, force=True)

    # TODO XXX - decide whether or not the instance was terminated
    return SUCCESS
