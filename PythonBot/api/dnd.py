import re

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth

from database.dnd import dnd, dndclass, dndsubclass, dndrace, dndsubrace, dndbackground, dndsource
from secret.api_secrets import route_start


def init_dnd(api: Flask, auth: HTTPBasicAuth):
    print('Adding dnd paths')

    # ----- /rpg/dnd
    def get_source_from_qp():
        try:
            return [int(x) for x in request.args.get('source').split(',')]
        except (ValueError, KeyError):
            return 'all'

    def get_json():
        r = request.json
        for f in ['id', 'source']:
            if r.get(f):
                r[f] = int(r.get(f))
        if r.get('enable'):
            r['enable'] = bool(r.get('enable'))
        return r

    @api.route(route_start + '/rpg/dnd/source', methods=['GET', 'POST'])
    @auth.login_required
    def dnd_sources():
        if request.method == 'POST':
            dnd.create_all(dnd.SOURCE_TABLE, get_json())
            return jsonify({})
        sources = dndsource.get_sources()
        return jsonify(sources)

    @api.route(route_start + '/rpg/dnd/source/<id>', methods=['GET'])
    @auth.login_required
    def dnd_source(id: str):
        if re.match('^[0-9]*$', id):
            c = dnd.get_all_by_id(dnd.SOURCE_TABLE, int(id))
        else:
            c = dnd.get_all_by_name(dnd.SOURCE_TABLE, id)
        return jsonify(c)

    @api.route(route_start + '/rpg/dnd/race', methods=['GET', 'POST'])
    @auth.login_required
    def dnd_races():
        if request.method == 'POST':
            dnd.create_all(dnd.RACE_TABLE, get_json())
            return jsonify({})
        races = dndrace.get_races(get_source_from_qp())
        return jsonify(races)

    @api.route(route_start + '/rpg/dnd/race/<id>', methods=['GET'])
    @auth.login_required
    def dnd_race(id: str):
        if re.match('^[0-9]*$', id):
            c = dnd.get_all_by_id(dnd.RACE_TABLE, int(id))
        else:
            c = dnd.get_all_by_name(dnd.RACE_TABLE, id)
        return jsonify(c)

    @api.route(route_start + '/rpg/dnd/subrace', methods=['GET', 'POST'])
    @auth.login_required
    def dnd_subraces():
        if request.method == 'POST':
            dnd.create_all(dnd.SUBRACE_TABLE, get_json())
            return jsonify({})
        subracees = dndsubrace.get_subraces(get_source_from_qp())
        return jsonify(subracees)

    @api.route(route_start + '/rpg/dnd/subrace/<id>', methods=['GET'])
    @auth.login_required
    def dnd_subrace(id: str):
        if re.match('^[0-9]*$', id):
            c = dnd.get_all_by_id(dnd.SUBRACE_TABLE, int(id))
        else:
            c = dnd.get_all_by_name(dnd.SUBRACE_TABLE, id)
        return jsonify(c)

    @api.route(route_start + '/rpg/dnd/class', methods=['GET', 'POST'])
    @auth.login_required
    def dnd_classes():
        if request.method == 'POST':
            dnd.create_all(dnd.CLASS_TABLE, get_json())
            return jsonify({})
        classes = dndclass.get_classes(get_source_from_qp())
        return jsonify(classes)

    @api.route(route_start + '/rpg/dnd/class/<id>', methods=['GET'])
    @auth.login_required
    def dnd_class(id: str):
        if re.match('^[0-9]*$', id):
            c = dnd.get_all_by_id(dnd.CLASS_TABLE, int(id))
        else:
            c = dnd.get_all_by_name(dnd.CLASS_TABLE, id)
        return jsonify(c)

    @api.route(route_start + '/rpg/dnd/subclass', methods=['GET', 'POST'])
    @auth.login_required
    def dnd_subclasses():
        if request.method == 'POST':
            dnd.create_all(dnd.SUBCLASS_TABLE, get_json())
            return jsonify({})
        subclasses = dndsubclass.get_subclasses(get_source_from_qp())
        return jsonify(subclasses)

    @api.route(route_start + '/rpg/dnd/subclass/<id>', methods=['GET'])
    @auth.login_required
    def dnd_subclass(id: str):
        if re.match('^[0-9]*$', id):
            c = dnd.get_all_by_id(dnd.SUBCLASS_TABLE, int(id))
        else:
            c = dnd.get_all_by_name(dnd.SUBCLASS_TABLE, id)
        return jsonify(c)

    @api.route(route_start + '/rpg/dnd/background', methods=['GET', 'POST'])
    @auth.login_required
    def dnd_backgrounds():
        if request.method == 'POST':
            dnd.create_all(dnd.BACKGROUND_TABLE, get_json())
            return jsonify({})
        backgrounds = dndbackground.get_backgrounds(get_source_from_qp())
        return jsonify(backgrounds)

    @api.route(route_start + '/rpg/dnd/background/<id>', methods=['GET'])
    @auth.login_required
    def dnd_background(id: str):
        if re.match('^[0-9]*$', id):
            c = dnd.get_all_by_id(dnd.BACKGROUND_TABLE, int(id))
        else:
            c = dnd.get_all_by_name(dnd.BACKGROUND_TABLE, id)
        return jsonify(c)
