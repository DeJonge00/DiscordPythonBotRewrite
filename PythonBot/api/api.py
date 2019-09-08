from flask import Flask, jsonify, make_response, request, abort
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from secret.secrets import api_username, api_password, APIAddress, APIPort
from datetime import datetime
from database.general import general, prefix, starboard, delete_commands, welcome
from database.general.general import DESC
from database.general.command_counter import get_command_counters
# from database.rpg import rpg
from database.dnd import dnd
import requests
from secret.secrets import prefix as default_prefix
import json

route_start = ''

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
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def page_from_query():
    return int(request.args.get('page', 1)), int(request.args.get('limit', 0))


# ----- /commands -----
@api.route(route_start + '/commands', methods=['GET'])
@auth.login_required
def get_command_counters():
    t = datetime.now().timestamp() - (24 * 60 * 60)  # Limit to 2 weeks of data
    return jsonify(list(get_command_counters(t)))


def resolve_channels(servers):
    c_table = general.get_table(general.CHANNEL_TABLE)
    for server in servers:
        for channel_type in ['text', 'voice']:
            server['channels'][channel_type] = [c_table.find_one({general.CHANNEL_ID: x}, {'_id': 0}) for x in
                                                server.get('channels').get(channel_type)]
    return servers


# ----- /servers -----
@api.route(route_start + '/servers', methods=['GET'])
@auth.login_required
def get_server_list():
    servers = general.get_server_list()
    if request.args.get('resolve_channels'):
        servers = resolve_channels(servers)
    return jsonify(servers)


@api.route(route_start + '/servers/<int:server_id>', methods=['GET'])
@auth.login_required
def get_server(server_id: int):
    r = general.get_server(server_id)
    if request.args.get('resolve_channels'):
        r = resolve_channels(r)[0]
    return jsonify(r)


@api.route(route_start + '/servers/<int:server_id>/config', methods=['GET'])
@auth.login_required
def get_server_config(server_id: int):
    server_id = str(server_id)
    welcome = general.get_table(general.WELCOME_TABLE).find_one({general.SERVER_ID: server_id}, {'_id': 0})
    if welcome:
        welcome = {
            'id': welcome.get(general.CHANNEL_ID),
            'text': welcome.get('message')
        }

    goodbye = general.get_table(general.GOODBYE_TABLE).find_one({general.SERVER_ID: server_id}, {'_id': 0})
    if goodbye:
        goodbye = {
            'id': goodbye.get(general.CHANNEL_ID),
            'text': goodbye.get('message')
        }
    server_prefix = prefix.get_prefix(int(server_id))
    if not server_prefix:
        server_prefix = default_prefix

    starchannel = starboard.get_star_channel(int(server_id))
    if not starchannel:
        starchannel = "None"

    return jsonify({
        'welcome': welcome,
        'goodbye': goodbye,
        'delete_commands': delete_commands.get_delete_commands(server_id),
        'star': starchannel,
        'prefix': server_prefix
    })


@api.route(route_start + '/servers/<int:server_id>/config', methods=['POST'])
@auth.login_required
def set_server_config(server_id: int):
    config_data = json.loads(request.data)
    if config_data.get('prefix'):
        prefix.set_prefix(server_id, config_data.get('prefix'))
    if config_data.get('star'):
        starboard.set_star_channel(server_id, config_data.get('star'))
    if config_data.get('welcome'):
        w = config_data.get('welcome')
        welcome.set_message(general.WELCOME_TABLE, server_id, w.get('id'), w.get('text'))
    if config_data.get('goodbye'):
        g = config_data.get('goodbye')
        welcome.set_message(general.GOODBYE_TABLE, server_id, g.get('id'), g.get('text'))
    if config_data.get('delete_commands'):
        b = True if config_data.get('delete_commands') == 'true' else False
        delete_commands.set_delete_commands(str(server_id), b)
    return jsonify({'Status': 'Success'})


# # ----- /rpg -----
# @api.route(route_start + '/rpg/players', methods=['GET'])
# @auth.login_required
# def get_rpg_players():
#     try:
#         page, per_page = page_from_query()
#     except ValueError:
#         return abort(400, {'error': 'invalid parameters'})
#     if not per_page:
#         per_page = 25
#     skip, amount = per_page * (page - 1), per_page
#     if amount <= 0 or skip < 0:
#         return abort(404)
#     r = rpg.get_table(rpg.RPG_PLAYER_TABLE).find({}, {'_id': 0}).sort('exp', DESC).skip(skip).limit(amount)
#     return jsonify(list(r))
#
#
# @api.route(route_start + '/rpg/players/count', methods=['GET'])
# @auth.login_required
# def get_rpg_players_count():
#     c = rpg.get_table(rpg.RPG_PLAYER_TABLE).count({})
#     return jsonify({'count': c})
#
#
# @api.route(route_start + '/rpg/players/<int:user_id>', methods=['GET'])
# @auth.login_required
# def get_rpg_player(user_id: int):
#     r = rpg.get_table(rpg.RPG_PLAYER_TABLE).find_one({'userid': str(user_id)}, {'_id': 0})
#     return jsonify(r)


# ----- /discord -----
discord_url = 'http://discordapp.com/api/'


# ----- /discord/users/@me -----
@api.route(route_start + '/discord/users/@me', methods=['GET'])
@auth.login_required
def get_discord_user():
    auth_token = request.args.get('token')
    if not auth_token:
        return jsonify({'Error': 'No auth given'})
    r = requests.get(discord_url + 'users/@me', headers={'Authorization': 'Bearer ' + auth_token})
    return jsonify(r.json())


# ----- /discord/users/@me/guilds
@api.route(route_start + '/discord/users/@me/guilds', methods=['GET'])
@auth.login_required
def get_discord_user_guilds():
    auth_token = request.args.get('token')
    if not auth_token:
        return jsonify({'Error': 'No auth given'})
    r = requests.get(discord_url + 'users/@me/guilds', headers={'Authorization': 'Bearer ' + auth_token})
    if r.status_code is not 200:
        return jsonify(r.json())
    player_servers = [x.get('id') for x in r.json()]
    bot_servers = general.get_table(general.SERVER_TABLE).find({general.SERVER_ID: {'$in': player_servers}}, {'_id': 0})
    bot_servers = resolve_channels(list(bot_servers))
    return jsonify(bot_servers)


# ----- /rpg/dnd
def get_source_from_qp():
    try:
        return [int(x) for x in request.args.get('source').split(',')]
    except (ValueError, KeyError):
        return 'all'


@api.route(route_start + '/rpg/dnd/source', methods=['GET'])
@auth.login_required
def get_dnd_source():
    sources = dnd.get_sources()
    return jsonify(sources)


@api.route(route_start + '/rpg/dnd/race', methods=['GET'])
@auth.login_required
def get_dnd_race():
    races = dnd.get_races(get_source_from_qp())
    return jsonify(races)


@api.route(route_start + '/rpg/dnd/class', methods=['GET'])
@auth.login_required
def get_dnd_class():
    classes = ['Artificer', 'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue',
               'Sorcerer', 'Warlock', 'Wizard']
    return jsonify(classes)


@api.route(route_start + '/rpg/dnd/subclass', methods=['GET'])
@auth.login_required
def get_dnd_subclass():
    subclasses = {
        'Artificer': ['Alchemist', 'Artillerist'],
        'Barbarian': ['Path of the Ancestral Guardian', 'Path of the Battlerager', 'Path of the Berserker'],
        'Bard': [],
        'Cleric': [],
        'Druid': [],
        'Fighter': [],
        'Monk': [],
        'Paladin': [],
        'Ranger': [],
        'Rogue': [],
        'Sorcerer': [],
        'Warlock': [],
        'Wizard': []
    }
    return jsonify(subclasses)


@api.route(route_start + '/rpg/dnd/background', methods=['GET'])
@auth.login_required
def get_dnd_background():
    backgrounds = dnd.get_backgrounds(get_source_from_qp())
    return jsonify(backgrounds)


# ----- Standard errors -----
@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({f'Error 404': 'Resource could not be found'}), 404)


if __name__ == '__main__':
    api.run(host=APIAddress, port=APIPort, debug=False)
