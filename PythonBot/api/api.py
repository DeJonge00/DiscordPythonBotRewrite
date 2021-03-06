from flask import Flask, jsonify, make_response
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

from api.commands import init_commands
from api.discord.users import init_users
from api.dnd import init_dnd
from api.rpg.players import init_rpg_players
from api.servers import init_servers
from secret.secrets import api_username, api_password


def setup():
    api = Flask(__name__)
    auth = HTTPBasicAuth()
    CORS(api)

    @auth.get_password
    def get_password(username):
        if username == api_username:
            return api_password
        return None

    @auth.error_handler
    def unauthorized():
        return make_response(jsonify({"error": "Unauthorized access"}), 401)

    init_commands(api, auth)
    init_servers(api, auth)
    init_rpg_players(api, auth)
    init_users(api, auth)
    init_dnd(api, auth)

    # ----- Standard errors -----
    @api.errorhandler(404)
    def not_found(error):
        return make_response(
            jsonify({f"Error 404": "Resource could not be found"}), 404
        )

    return api
