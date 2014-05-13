from slaveapi.slave import Slave
from slaveapi.actions.reboot import reboot
from slaveapi.actions.shutdown_buildslave import shutdown_buildslave
from .results import SUCCESS, FAILURE
from ..global_state import config
from ..clients.slavealloc import update_slave as update_slave_in_slavealloc

import logging
log = logging.getLogger(__name__)

def disable(name, reason_comment=None, use_force=None):
    """Attempts to disable the named slave from buildbot.

    Details of what was attempted and the result are reported into the
    slave's problem tracking bug at the end.

    Disabling is done in a series of steps outlined below:

    1. Disable In Slavealloc: unchecks enabled box for slave in slavealloc

    2. Stop Buildbot Process: stops buildbot process if one is running by
    either using graceful_shutdown or more aggressively decided upon a
    force_disable flag

    3. Verify Buildbot Process is Not Running: if buildbot process can't be
    confirmed dead, force a reboot

    4. Update Problem Tracking Bug: reopen problem tracking bug and leave
    comment if a 'comment' field was passed

    args:
        name (str) -- hostname of slave
        reason_comment (str) -- reason we wish to disable slave
        use_force (bool) -- if true and buildslave proc can't be killed
            gracefully, reboot the slave
    """
    action_succeeded_so_far = True
    status_msgs = ["Disabling Slave: %s" % name]
    result_status = SUCCESS  # innocent until proven guilty!

    slave = Slave(name)
    slave.load_slavealloc_info()
    slave.load_bug_info(createIfMissing=False)

    if not slave.enabled:  # slave disabled in slavealloc, nothing to do!
        status_msgs.append("Slave is already disabled. Nothing to do.")
        return result_status, "\n".join(status_msgs)

    #### 1. Disable Slave in Slavealloc
    status_msgs.append("disabling in slavealloc")
    slavealloc_values = {
        'enabled': 0,
    }
    update_alloc_result, update_alloc_msg = update_slave_in_slavealloc(
        api=config["slavealloc_api_url"], name=name,
        values_to_update=slavealloc_values,
    )
    if update_alloc_result is FAILURE:
        action_succeeded_so_far = False
    ####

    status_msgs.append(str(update_alloc_msg))

    if action_succeeded_so_far:
        #### 2. Stop Buildbot Process
        stop_buildslave_result, stop_buildslave_msg = shutdown_buildslave(name)
        ####

        #### 3. Verify Buildbot Process is Not Running
        if stop_buildslave_result is FAILURE:
            status_msgs.append(str(stop_buildslave_msg))
            if use_force:
                # off with his head!
                status_msgs.append("Forcing a reboot.")
                # don't let reboot() update bug; we will do it at end of action
                reboot_result, reboot_msg = reboot(name, update_bug=False)
                if reboot_result is FAILURE:
                    action_succeeded_so_far = False
                status_msgs.append(str(reboot_msg))
            else:
                action_succeeded_so_far = False
        ####

    #### 4. Update Problem Tracking Bug
    if action_succeeded_so_far:
        status_msgs.append("%s - was successfully disabled via slaveapi" % name)
        if reason_comment:
            status_msgs.append("Reason for disabling: %s" % reason_comment)
    else:
        status_msgs.append("%s - was not disabled via Slaveapi" % name)
        result_status = FAILURE

    result_msg = "\n".join(status_msgs)
    bug_data = {}
    if not slave.bug.data["is_open"]:
        bug_data["status"] = "REOPENED"
    slave.bug.add_comment(result_msg, data=bug_data)
    ####

    return result_status, result_msg
