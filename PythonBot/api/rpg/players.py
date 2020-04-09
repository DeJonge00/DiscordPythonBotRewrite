from flask import Flask, jsonify, request, abort
from flask_httpauth import HTTPBasicAuth

from api.api import route_start
from api.helper_functions import page_from_query
from database.rpg import rpg_main

ASC = 1
DESC = -1


def init_rpg_players(api: Flask, auth: HTTPBasicAuth):
    @api.route(route_start + '/rpg/players', methods=['GET'])
    @auth.login_required
    def get_rpg_players():
        try:
            page, per_page = page_from_query(request)
        except ValueError:
            return abort(400, {'error': 'invalid parameters'})
        if not per_page:
            per_page = 25
        skip, amount = per_page * (page - 1), per_page
        if amount <= 0 or skip < 0:
            return abort(404)
        r = rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).find({}, {'_id': 0}).sort('exp', DESC).skip(skip).limit(amount)
        return jsonify(list(r))

    @api.route(route_start + '/rpg/players/count', methods=['GET'])
    @auth.login_required
    def get_rpg_players_count():
        c = rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).count({})
        return jsonify({'count': c})

    @api.route(route_start + '/rpg/players/<int:user_id>', methods=['GET'])
    @auth.login_required
    def get_rpg_player(user_id: int):
        r = rpg_main.get_table(rpg_main.RPG_PLAYER_TABLE).find_one({'userid': str(user_id)}, {'_id': 0})
        return jsonify(r)
