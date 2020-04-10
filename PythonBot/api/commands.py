from flask import Flask, jsonify, make_response, request, abort
from flask_httpauth import HTTPBasicAuth
from datetime import datetime

from api.api import route_start


def init_commands(api: Flask, auth: HTTPBasicAuth):
    @api.route(route_start + '/commands', methods=['GET'])
    @auth.login_required
    def get_command_counters():
        t = datetime.now().timestamp() - (24 * 60 * 60)  # Limit to 2 weeks of data
        return jsonify(list(get_command_counters(t)))