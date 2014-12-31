import logging

from ..clients import aws

log = logging.getLogger(__name__)


def aws_terminate_instance(name):
    """Attempts to terminate an aws instance


    :param name: hostname of slave

    :rtype: tuple
    """
    # TODO update problem tracking bug if one exists
    status_msgs = ["Terminating aws instance: `{0}`\n".format(name)]
    return_code, terminate_msg = aws.terminate_instance(name)

    return return_code, "\n".join(status_msgs)
