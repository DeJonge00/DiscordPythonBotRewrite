from database.general.auto_voice_channel import get_joiner_channels, get_created_channels, set_created_channel, \
    set_joiner_channel

from discord import Member, VoiceChannel, VoiceState, Forbidden


async def new_voice_channel(joiner: VoiceChannel):
    name = '➡' + joiner.name[1:] if joiner.name else '➡General'
    reason = 'Auto voice channel: Created subchannel'
    return await joiner.guild.create_voice_channel(name, category=joiner.category, reason=reason)


async def check_vc(vc: VoiceChannel):
    if not vc.members:
        await vc.delete(reason='Auto voice channel: channel is empty')
        set_created_channel(vc.guild.id, vc.id, False)
        return


async def auto_channel(member: Member, before: VoiceState, after: VoiceState):
    if after.channel and after.channel.id in get_joiner_channels(member.guild.id):
        new_vc = await new_voice_channel(after.channel)
        set_created_channel(member.guild.id, new_vc.id)
        try:
            await member.move_to(new_vc)
        except Forbidden:
            pass
    if before.channel and before.channel.id in get_created_channels(member.guild.id):
        await check_vc(before.channel)


def deleted_channel(channel: VoiceChannel):
    if channel.id in get_joiner_channels(channel.guild.id):
        set_joiner_channel(channel.guild.id, channel.id, False)