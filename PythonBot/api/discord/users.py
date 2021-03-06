import requests
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth

from api.helper_functions import resolve_channels
from database.general import general
from secret.api_secrets import route_start, discord_url


def init_users(api: Flask, auth: HTTPBasicAuth):
    print("Adding users paths")

    # ----- /discord/users/@me -----
    @api.route(route_start + "/discord/users/@me", methods=["GET"])
    @auth.login_required
    def get_discord_user():
        auth_token = request.args.get("token")
        if not auth_token:
            return jsonify({"Error": "No auth given"})
        r = requests.get(
            discord_url + "users/@me", headers={"Authorization": "Bearer " + auth_token}
        )
        return jsonify(r.json())

    # ----- /discord/users/@me/guilds
    @api.route(route_start + "/discord/users/@me/guilds", methods=["GET"])
    @auth.login_required
    def get_discord_user_guilds():
        auth_token = request.args.get("token")
        if not auth_token:
            return jsonify({"Error": "No auth given"})
        r = requests.get(
            discord_url + "users/@me/guilds",
            headers={"Authorization": "Bearer " + auth_token},
        )
        if r.status_code is not 200:
            print("get_discord_user_guilds returned status code", r.status_code)
            return jsonify(r.json())

        player_servers = [str(x.get("id")) for x in r.json()]
        bot_servers = general.get_table(general.SERVER_TABLE).find(
            {general.SERVER_ID: {"$in": player_servers}}, {"_id": 0}
        )
        bot_servers = resolve_channels(list(bot_servers))
        return jsonify(bot_servers)
