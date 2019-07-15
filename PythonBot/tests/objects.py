from discord import Attachment, User
from discord.state import ConnectionState


def get_test_connection_state():
    return ConnectionState(dispatch=None, chunker=None, handlers=None, syncer=None, http=None, loop=None)


def get_test_attachment(url: str):
    return Attachment(data={
        'url': url,
        'id': 123,
        'size': 1,
        'filename': 'filename'
    }, state=get_test_connection_state())


def get_test_user(username: str):
    return User(data={
        'username': username,
        'id': 123,
        'discriminator': 1234,
        'avatar': 'avatar_picture'
    }, state=get_test_connection_state())
