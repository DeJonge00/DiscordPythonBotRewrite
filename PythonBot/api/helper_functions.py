from database.general import general


def resolve_channels(servers):
    c_table = general.get_table(general.CHANNEL_TABLE)
    for server in servers:
        for channel_type in ['text', 'voice']:
            server['channels'][channel_type] = [c_table.find_one({general.CHANNEL_ID: x}, {'_id': 0}) for x in
                                                server.get('channels').get(channel_type)]
    return servers


def page_from_query(request):
    return int(request.args.get('page', 1)), int(request.args.get('limit', 0))
