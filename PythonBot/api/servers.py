import json

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth

from api.helper_functions import resolve_channels
from database.general import general, prefix, starboard, delete_commands, welcome
from secret.api_secrets import route_start
from secret.secrets import prefix as default_prefix


def init_servers(api: Flask, auth: HTTPBasicAuth):
    print('Adding servers paths')

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
