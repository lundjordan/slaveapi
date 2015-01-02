from flask import Flask

from .results import Results
from .slave import Reboot, Slave, ShutdownBuildslave, GetUptime, GetLastActivity
from .slave import Disable, AWSTerminateInstance, AWSStartInstance, AWSStopInstance
from .slave import AWSInstanceStatus
from .slaves import Slaves

app = Flask(__name__)

app.add_url_rule("/results", view_func=Results.as_view("results"), methods=["GET"])
app.add_url_rule("/slaves", view_func=Slaves.as_view("slaves"), methods=["GET"])
app.add_url_rule("/slaves/<slave>", view_func=Slave.as_view("slave"), methods=["GET"])
app.add_url_rule("/slaves/<slave>/actions/reboot", view_func=Reboot.as_view("reboot"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/get_uptime", view_func=GetUptime.as_view("get_uptime"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/get_last_activity", view_func=GetLastActivity.as_view("get_last_activity"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/shutdown_buildslave", view_func=ShutdownBuildslave.as_view("shutdown_buildslave"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/disable", view_func=Disable.as_view("disable"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/terminate", view_func=AWSTerminateInstance.as_view("aws_terminate_instance"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/start", view_func=AWSStartInstance.as_view("aws_start_instance"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/stop", view_func=AWSStopInstance.as_view("aws_stop_instance"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/status", view_func=AWSInstanceStatus.as_view("aws_instance_type"), methods=["GET", "POST"])
