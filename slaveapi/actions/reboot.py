from .results import SUCCESS, FAILURE
from ..clients.bugzilla import file_reboot_bug
from ..clients.ping import ping
from ..slave import Slave, wait_for_reboot, get_console

import logging
log = logging.getLogger(__name__)

def reboot(name):
    """Attempts to reboot the named slave a series of ways, escalating from
    peacefully to mercilessly. Details of what was attempted and the result
    are reported into the slave's problem tracking bug at the end. Reboots
    are attempted through the following means (from most peaceful to least
    merciful):

    * SSH: Logs into the machine via SSH and reboots it with an \
        appropriate command.

    * IPMI: Uses the slave's IPMI interface to initiate a hard \
        reboot. If the slave has no IPMI interface, this is skipped.

    * PDU: Powercycles the slave by turning off the power, and then \
        turning it back on.

    * Bugzilla: Requests that IT reboot the slave by updating or creating \
        the appropriate bugs.
    """
    status_text = ""
    slave = Slave(name)
    slave.load_inventory_info()
    slave.load_ipmi_info()
    slave.load_bug_info(createIfMissing=False)
    status_text += "Attempting SSH reboot..."

    alive = False
    # If the slave is pingable, try an SSH reboot...
    try:
        if ping(slave.fqdn):
            console = get_console(slave)
            console.reboot()
            alive = wait_for_reboot(slave)
    except:
        log.exception("%s - Caught exception during SSH reboot.", name)

    # If that doesn't work, maybe an IPMI reboot will...
    if not alive and slave.ipmi:
        status_text += "Failed.\n"
        status_text += "Attempting IPMI reboot..."
        try:
            slave.ipmi.powercycle()
            alive = wait_for_reboot(slave)
        except:
            log.exception("%s - Caught exception during IPMI reboot.", name)

    # Mayhaps a PDU reboot?
    if not alive and slave.pdu:
        status_text += "Failed.\n"
        status_text += "Attempting PDU reboot..."
        try:
            slave.pdu.powercycle()
            alive = wait_for_reboot(slave)
        except:
            log.exception("%s - Caught exception during PDU reboot.", name)

    if alive:
        # To minimize bugspam, no comment is added to the bug if we were
        # able to bring it back up.
        status_text += "Success!"
        return SUCCESS, status_text
    else:
        status_text += "Failed.\n"
        if slave.reboot_bug:
            status_text += "Slave already has reboot bug (%s), nothing to do." % slave.reboot_bug.id_
            return FAILURE, status_text
        else:
            if not slave.bug:
                slave.load_bug_info(createIfMissing=True)
            slave.reboot_bug = file_reboot_bug(slave)
            status_text += "Filed IT bug for reboot (bug %s)" % slave.reboot_bug.id_
            data = {}
            if not slave.bug.data["is_open"]:
                data["status"] = "REOPENED"
            slave.bug.add_comment(status_text, data=data)
            return FAILURE, status_text
