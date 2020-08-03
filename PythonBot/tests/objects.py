from discord import Attachment, User, Emoji, Guild
from discord.state import ConnectionState


def get_test_connection_state():
    return ConnectionState(
        dispatch=None, chunker=None, handlers=None, syncer=None, http=None, loop=None
    )


def get_test_attachment(url: str):
    return Attachment(
        data={"url": url, "id": 123, "size": 1, "filename": "filename"},
        state=get_test_connection_state(),
    )


def get_test_guild(name: str):
    return Guild(data={"id": 1234}, state=get_test_connection_state())


def get_test_user(username: str):
    return User(
        data={
            "username": username,
            "id": 123,
            "discriminator": 1234,
            "avatar": "avatar_picture",
        },
        state=get_test_connection_state(),
    )


def get_test_emoji(name: str, id: int):
    return Emoji(
        guild=get_test_guild("test_guild"),
        state=get_test_connection_state(),
        data={"require_colons": True, "managed": True, "id": id, "name": name},
    )
