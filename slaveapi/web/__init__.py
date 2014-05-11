from flask import Flask

from .results import Results
from .slave import Reboot, Slave, ShutdownBuildslave, GetUptime, GetLastActivity
from .slave import Update
from .slaves import Slaves

app = Flask(__name__)

app.add_url_rule("/results", view_func=Results.as_view("results"), methods=["GET"])
app.add_url_rule("/slaves", view_func=Slaves.as_view("slaves"), methods=["GET"])
app.add_url_rule("/slaves/<slave>", view_func=Slave.as_view("slave"), methods=["GET"])
app.add_url_rule("/slaves/<slave>/actions/reboot", view_func=Reboot.as_view("reboot"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/get_uptime", view_func=GetUptime.as_view("get_uptime"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/get_last_activity", view_func=GetLastActivity.as_view("get_last_activity"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/shutdown_buildslave", view_func=ShutdownBuildslave.as_view("shutdown_buildslave"), methods=["GET", "POST"])
app.add_url_rule("/slaves/<slave>/actions/update", view_func=Update.as_view("update"), methods=["GET", "POST"])
