import logging

from ..clients import aws

log = logging.getLogger(__name__)


def aws_instance_status(name):
    """Attempts to query an aws instance and return its current status


    :param name: hostname of slave

    :rtype: tuple of status, msg
    """
    return aws.instance_status(name)
