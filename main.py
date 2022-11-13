import discord
import json

try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    print("An error has occured reading the config")
    print("\t" + str(e))

exported = {}

users = []
users_json = []

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Successfully logged in as {client.user}')

@client.event
async def on_message(message):
    # if the message is "$archive" and is sent by the owner(if that's required), continue
    if(not (message.content == config["archive-command"])):
        return
    if (not (not config["admin-required"] or message.author.id == message.guild.owner_id)):
        await message.reply("Seems like you are not the owner, so you are unable to execute this command.")
        return

    await message.reply(f"Starting the export of {message.guild}...")

    channels_export = []
    guild = await client.fetch_guild(message.guild.id, with_counts=True) # default is True, but just in case
    efname = "export-" + str(guild.id)

    text_channels = getChannels(guild.id, ctype="text")
    for channel in text_channels:
        messages = [message async for message in channel.history(limit=None)]
        channels_export.append({
            "type"                          : "text",
            "name"                          : channel.name,
            "id"                            : channel.id,
            "category_id"                   : channel.category_id,
            "topic"                         : channel.topic,
            "position"                      : channel.position,
            "slowmode_delay"                : channel.slowmode_delay,
            "nsfw"                          : channel.nsfw,
            "default_auto_archive_duration" : channel.default_auto_archive_duration,
            "messages"                      : [getMessageJSON(message) for message in messages],
            "is_news"                       : channel.is_news(),
            "created_at"                    : str(channel.created_at),
            })
        print(f"found {len(messages)} messages in {channel}")

    voice_channels = getChannels(guild.id, ctype="voice")
    for channel in voice_channels:
        channels_export.append({
            "type"               : "voice",
            "bitrate"            : channel.bitrate,
            "category_id"        : channel.category_id,
            "created_at"         : str(channel.created_at),
            "id"                 : channel.id,
            "name"               : channel.name,
            "nsfw"               : channel.nsfw,
            "position"           : channel.position,
            "rtc_region"         : channel.rtc_region,
            "user_limit"         : channel.user_limit,
            "video_quality_mode" : str(channel.video_quality_mode)
            })

    # creating giant exported dictionary
    exported = {
            "afk_timeout" : guild.afk_timeout,
            "approximate_member_count" : guild.approximate_member_count,
            "approximate_presence_count" : guild.approximate_presence_count,
            "premium_progress_bar_enabled" : guild.premium_progress_bar_enabled,
            "banner"                       : guild.banner,
            "bitrate_limit"                : guild.bitrate_limit,
            "guild_id" : guild.id,
            "channels" : channels_export,
            "users"    : users_json
            }
    print("Done reading, writing to file...")
    with open(efname+".json", "w") as f:
        json.dump(exported, f)
    with open(efname+"-pretty.json", "w") as f:
        json.dump(exported, f, indent=4)

    await message.channel.send("Done exporting!")
    print("Done!")

def getChannels(gid: int, ctype: str = "text") -> dict:
    """Returns channels of a specified type for a given guild id.
    
    Fetches and returns channels of a specified type (by default type "text")
    given a valid guild id. It requires an initialized discord client object.

    Args:
        gid: the id of the guild, should be an int
        ctype:
            default value "text", only returns channels with this specified type.

    Returns:
        Returns an array of discord.abc.GuildChannel objects that have the type
        specified by the ctype argument.
    """
    text_channel_list = []
    for channel in client.get_guild(gid).channels:
        if str(channel.type) == ctype:
            text_channel_list.append(channel)

    return text_channel_list 

def getMessageJSON(message: discord.Message) -> dict:
    """Returns a JSON compatible dictionary given a message.
   
   Serializes a discord.Message object to valid dictionary that can be exported
   as JSON. It does not require a valid discord client running. The returned
   dictionary contains all important attributes of the discord.Message class.

    Args:
        message: a discord message object, type discord.Message.

    Returns:
        Returns a JSON serializable dictionary.
    """
    if not message.author.id in users:
        users.append(message.author.id)
        users_json.append(getUserJSON(message.author))
    return {
            "attachments" : [str(attachment) for attachment in message.attachments],
            "author"      : message.author.id, 
            "content"     : message.content,
            "created_at"  : str(message.created_at),
            "edited_at"   : str(message.edited_at),
            "id"          : message.id,
            # todo: embed
            "flags"       : message.flags.value,
            "pinned"      : message.pinned,
            "reactions"   : [getReactionJSON(reaction) for reaction in message.reactions ],
            "reference"   : getReferenceJSON(message.reference), 
            "stickers"    : [sticker.url for sticker in message.stickers],
            "type"        : str(message.type)
    }

def getUserJSON(author: discord.abc.User) -> dict:
    """Returns a JSON compatible dictionary given an author object.

    Makes a serializable dictionary given a discord.abc.User type object that 
    can be exported to JSON. The resulting dictionary is a valid representation
    of the given object. The method does not require a valid discord client
    running.

    Args:
        author: a valid discord.abc.User implementating object.

    Returns:
        Returns a JSON serializable dictionary.
    """
    return {
            "name"           : author.name,
            "id"             : author.id,
            "accent_color"   : str(author.accent_color),
            "avatar"         : str(author.avatar), 
            "banner"         : str(author.banner),
            "bot"            : author.bot,
            "color"          : str(author.color),
            "created_at"     : str(author.created_at),
            "default_avatar" : str(author.default_avatar),
            "discriminator"  : author.discriminator,
            "display_avatar" : str(author.display_avatar),
            "display_name"   : author.display_name,
            "id"             : author.id,
            "name"           : author.name,
            "public_flags"   : author.public_flags.value,
            "system"         : author.system
    }

def getReactionJSON(reaction: discord.Reaction) -> dict:
    return {
            "count" : reaction.count,
            "emoji" : str(reaction.emoji)
    }

def getReferenceJSON(reference: discord.MessageReference) -> dict:
    """Returns a JSON serializable dictionary given a reference object.

    Makes a JSON serializable python dictionary representation of a given
    discord.MessageReference object.

    Args:
        reference: a discord.MessageReference type object

    Returns:
        Returns a valid JSON serializable dictionary representation of the
        passed in object.

    """
    if (reference == None): return None
    else: return {
        "message_id"         : reference.message_id,
        "channel_id"         : reference.channel_id,
        "fail_if_not_exists" : reference.fail_if_not_exists
    }

try:
    client.run(config["token"])
except Exception as e:
    print("An exception has occured while logging in:")
    print("\t" + str(e))
