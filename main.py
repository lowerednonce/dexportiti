#!/usr/bin/python3
import discord
import json
import sys
import os.path

try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    print("An error has occured reading the config")
    print("\t" + str(e))

users = []
users_json = []

intents = discord.Intents.all()

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
    guild = await client.fetch_guild(message.guild.id, with_counts=True)
    # default is True, but just in case
    efname = "export-" + str(guild.id)

    text_channels = getChannels(guild.id, ctype="text")
    for channel in text_channels:
        messages = [message async for message in channel.history(limit=None)]
        threads = channel.threads
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
            "messages"                      : [await getMessageJSON(message) for message in messages],
            "threads"                       : [await getThreadJSON(thread) for thread in threads],
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
    try:
        exported = {
                "afk_timeout"                  : guild.afk_timeout,
                "approximate_member_count"     : guild.approximate_member_count,
                "approximate_presence_count"   : guild.approximate_presence_count,
                "premium_progress_bar_enabled" : guild.premium_progress_bar_enabled,
                "banner"                       : guild.banner,
                "bitrate_limit"                : guild.bitrate_limit,
                "created-at"                   : str(guild.created_at),
                "description"                  : guild.description,
                "discovery_splash"             : await getAssetJSON(guild.discovery_splash),
                "emoji_limit"                  : guild.emoji_limit,
                "features"                     : guild.features,
                "filesize_limit"               : guild.filesize_limit,
                "icon"                         : await getAssetJSON(guild.icon),
                "id"                           : guild.id,
                "large"                        : guild.large,
                "max_members"                  : guild.max_members,
                "max_presences"                : guild.max_presences,
                "max_video_channel_users"      : guild.max_video_channel_users,
                "member_count"                 : guild.member_count,
                "members"                      : [getUserJSON(member) async for member in guild.fetch_members(limit=None)],
                "name"                         : guild.name,
                "mfa_level"                    : str(guild.mfa_level),
                "nsfw_level"                   : str(guild.nsfw_level),
                "owner_id"                     : guild.owner_id,
                "preferred_locale"             : str(guild.preferred_locale),
                "premium_progress_bar_enabled" : guild.premium_progress_bar_enabled,
                "premium_subscribers"          : [getUserJSON(subscriber) for subscriber in guild.premium_subscribers],
                "premium_subscription_count"   : guild.premium_subscription_count, # don't ask why not take a len()
                "premium_tier"                 : guild.premium_tier,
                "splash"                       : await getAssetJSON(guild.splash),
                "sticker_limit"                : guild.sticker_limit,
                "system_channel_flags"         : guild.system_channel_flags.value,
                "unavailable"                  : guild.unavailable,
                "vanity_url"                   : guild.vanity_url,
                "vanity_url_code"              : guild.vanity_url_code,
                "verification_level"           : str(guild.verification_level),
                "widget_enabled"               : guild.widget_enabled,
                "audit_log"                    : [getAuditLogEntryJSON(entry) async for entry in guild.audit_logs(limit=None)],

                # TODO emojis explicit_content_filter premium_subscriber_role public_updates_channel roles rules_channel scheduled_events stickers system_channel
                # TODO stage stuff

                # manually exported channels
                "channels"                     : channels_export,
                "active-users"                 : users_json
        }
        

        print("Done reading, writing to file...")
        with open(efname+".json", "w") as f:
            json.dump(exported, f)
        with open(efname+"-pretty.json", "w") as f:
            json.dump(exported, f, indent=4)
    
        await message.channel.send("Done exporting!")
        print("Done!")
    except Exception as e:
        error_message = f"Error occured while exporting, on line {sys.exc_info()[2].tb_lineno}\n"
        error_message += str(e)
        await message.channel.send(error_message)
        print("Exception in on_message")
        print(sys.exc_info()[2])

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

async def getMessageJSON(message: discord.Message) -> dict:
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
            "attachments" : [await getAttachmentJSON(attachment) for attachment in message.attachments],
            "author"      : message.author.id, 
            "content"     : message.content,
            "created_at"  : str(message.created_at),
            "edited_at"   : str(message.edited_at),
            "id"          : message.id,
            # TODO embed
            "flags"       : message.flags.value,
            "pinned"      : message.pinned,
            "reactions"   : [await getReactionJSON(reaction) for reaction in message.reactions ],
            "reference"   : getReferenceJSON(message.reference), 
            "stickers"    : [sticker.url for sticker in message.stickers],
            "type"        : str(message.type)
    }

async def getAttachmentJSON(attachment: discord.Attachment) -> dict:
    """Returns a JSON serializable dictionary given an asset object.

    Returns and optionally saves the passed in asset object of type
    discord.Attachment. It saves the asset if the "save-assets" option is set
    to True in the config, if it is, it will save to the directory specified
    by the "asset-save-path" config option.

    Args:
        asset: a Discord asset object of type discord.Attachment

    Returns:
        Returns a JSON serializable dictionary representation of the argument
    """
    if (attachment == None): return None # we might get a None object in
    filename = config["asset-save-path"] + "/attachments/" + str(attachment.id) + "-" + attachment.filename
    if (config["save-assets"] and not os.path.exists(filename)):
        try:
            print(f"[DEBUG] downloading asset to filename {filename}")
            await attachment.save(filename)
            # use_cached only works after only a few minutes, only slows the download down
        except Exception as e:
            print("[DEBUG] failed saving asset")
            print(str(e))

    return {
            "id"           : attachment.id,
            "size"         : attachment.size,
            "height"       : attachment.height,
            "width"        : attachment.width,
            "filename"     : attachment.filename,
            "url"          : attachment.url,
            "content_type" : attachment.content_type,
            "description"  : attachment.description,
            "ephemeral"    : attachment.ephemeral,
            "is_spoiler"   : attachment.is_spoiler(),
    }

async def getAssetJSON(asset:discord.Attachment) -> dict:
    if (asset == None): return None # we might get a None object in
    filename = config["asset-save-path"] + "/assets/" + asset.key
    if (config["save-assets"] and not os.path.exists(filename)):
        try:
            print(f"[DEBUG] downloading asset to filename {filename}")
            await asset.save(filename)
            # use_cached only works after only a few minutes, only slows the download down
        except Exception as e:
            print("[DEBUG] failed saving asset")
            print(str(e))
    return {"key" : asset.key}

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

async def getReactionJSON(reaction: discord.Reaction) -> dict:
    return {
            "count" : reaction.count,
            "emoji" : str(reaction.emoji),
            "users" : [user.id async for user in reaction.users()]
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
    if (reference == None):
        return None
    else:
        return {
            "message_id"         : reference.message_id,
            "channel_id"         : reference.channel_id,
            "fail_if_not_exists" : reference.fail_if_not_exists
        }


async def getThreadJSON(thread: discord.Thread) -> dict:
    """Parses a Thread into a JSON serializable dictionary.

    Takes a discord.Thread object, and represents it as a valid
    JSON-serializable python dictionary. It does not require a
    valid discord client object.

    Args:
        thread: a discord.Thread object to be parsed

    Returns:
        Returns a valid JSON serializable dictionary representation of the
        passed in thread object.
    """
    return {
        "archive_timestamp"     : str(thread.archive_timestamp),
        "archived"              : thread.archived,
        "archiver_id"           : thread.archiver_id,
        "auto_archive_duration" : thread.auto_archive_duration,
        "created_at"            : str(thread.created_at),
        "flags"                 : thread.flags.value,
        "id"                    : thread.id,
        "invitable"             : thread.invitable,
        "locked"                : thread.locked,
        "member_count"          : thread.member_count,
        "name"                  : thread.name,
        "owner_id"              : thread.owner_id,
        "parent_id"             : thread.parent_id,
        "slowmode_delay"        : thread.slowmode_delay,
        "type"                  : str(thread.type),
        "thread_members"        : [getThreadMemberJSON(member) for member in await thread.fetch_members()],
        "is_nsfw"               : thread.is_nsfw(),
        "is_news"               : thread.is_news(),
        "messages"              : [await getMessageJSON(message) async for message in thread.history(limit=None)]
    }

def getThreadMemberJSON(member: discord.ThreadMember) -> dict:
    return {
            "id"        : member.id,
            "joined_at" : str(member.joined_at)
    }

def getAuditLogEntryJSON(entry: discord.AuditLogEntry) -> dict:
    """Parses audit log entry to a JSON serializable dictionary

    Args:
        entry:a singular log entry of type discord.AuditLogEntry

    Returns:
        Returns a valid JSON serializable representation of the passed in log entry
    """
    return {
            "action" : str(entry.action),
            "user"   : entry.user.id,
            "id"     : entry.id,
            # TODO target extra
            "reason" : entry.reason,
            "created_at" : str(entry.created_at),
            "category"   : str(entry.category),
            # will not implement entry.before and entry.after
    }

if __name__ == "__main__":
    try:
        client.run(config["token"])
    except Exception as e:
        print("An exception has occured while logging in:")
        print("\t" + str(e))
