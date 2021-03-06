from datetime import datetime

from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth

from database.general.command_counter import get_command_counters
from secret.api_secrets import route_start


def init_commands(api: Flask, auth: HTTPBasicAuth):
    print("Adding commands path")

    @api.route(route_start + "/commands", methods=["GET"])
    @auth.login_required
    def command_counters():
        # TODO: fix
        t = datetime.now().timestamp() - (24 * 60 * 60)  # Limit to 2 weeks of data
        return jsonify(list(get_command_counters(t)))

    @api.route(route_start + "/health", methods=["GET"])
    def are_u_ok():
        return "I'm ok"
