#!/usr/bin/python3
import datetime
import discord
import os.path
import shutil
import json
import sys
import os

try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    print("An error has occured reading the config")
    print("\t" + str(e))
    exit(-1) # this is quite fatal

# set up bot
intents = discord.Intents.all()

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

def user_authorized(guild: discord.Guild, user: discord.User) -> bool:
    if (user.id == guild.owner_id):
        return True # server owners are always authorized
    else:
        if (not guild.id in settings.keys()):
            # no settings for server
            return False
        for role_id in settings[guild.id]:
            if (role_id in [role.id for role in user.roles]):
                return True
        return False # no matching role found


@client.event
async def on_ready():
    tree.add_command(archive)
    tree.add_command(Settings())
    tree.add_command(remove_archive)
    await tree.sync()
    print(f'Successfully logged in as {client.user}')


class Settings(discord.app_commands.Group):
    @discord.app_commands.command(
            name="add_role",
            description="Make a role be able to export on your server",
            )
    async def add_role(self, interaction: discord.Interaction, role: discord.Role):
        if (not user_authorized(interaction.guild, interaction.user)):
            await interaction.response.send_message("Seems like you are not authorized to do this.", ephemeral=True)
            return
        if (interaction.guild.id in settings.keys()):
            if (role.id in settings[interaction.guild_id]):
                await interaction.response.send_message("Role already authorized.", ephemeral=True)
                return
        else:
            settings[interaction.guild_id] = []
    
        settings[interaction.guild_id].append(role.id)
        dump_settings(settings)
        await interaction.response.send_message(f"Successfully added \"{role.name}\" to the list of roles allowed to export your server!")
    
    @discord.app_commands.command(
            name="remove_role",
            description="Remove role from being able to archive your server"
            )
    async def remove_role(self, interaction: discord.Interaction, role: discord.Role):
        if (not user_authorized(interaction.guild, interaction.user)):
            await interaction.response.send_message("Seems like you are not authorized to do this.", ephemeral=True)
            return
    
        if (interaction.guild_id in settings.keys()):
            if (not (role.id in settings[interaction.guild_id])):
                await interaction.response.send_message("Role already unauthorized.", ephemeral=True)
                return
        else:
            settings[interaction.guild_id] = []
            await interaction.response.send_message("Role already unauthorized.", ephemeral=True)
            return
    
        settings[interaction.guild_id].remove(role.id)
        dump_settings(settings)
        await interaction.response.send_message(f"Successfully removed \"{role.name}\" from list of authorized roles.")

    @discord.app_commands.command(
            name="list_roles",
            description="List the roles currently authorized to archive your server."
            )
    async def list_roles(self, interaction: discord.Interaction):
        # no authorization needed

        if (not interaction.guild_id in settings.keys()):
            interaction.response.send_message("No settings for this server.")
            return

        response = "The list of roles allowed to manage archives: \n"
        if (not interaction.guild_id in settings.keys()):
            response += "no roles for this server"
        else:
            names_list = [role.name for role in interaction.guild.roles if role.id in settings[interaction.guild_id]]
            for name in names_list:
                response += "- " + name + "\n"

        await interaction.response.send_message(response)


@discord.app_commands.command(
        name="remove",
        description="remove active server archive, might fix bugs"
        )
async def remove_archive(interaction: discord.Interaction):
    if (not user_authorized(interaction.guild, interaction.user)):
        await interaction.response.send_message("Seems like you are not authorized to do this. Ask the server owner to add a role that authorized, or to make one authorized.", ephemeral=True)
        return
    
    if ( not os.path.exists(str(interaction.guild_id))):
        await interaction.response.send_message("No export found, run the /archive command first to get an archive exported.", ephemeral=True)
        return

    shutil.move(str(interaction.guild_id), ".removed_" + str(interaction.guild_id) + "_" + str(datetime.datetime.today().timestamp()))
    await interaction.response.send_message("Success!")

@discord.app_commands.command(
        name="archive",
        description="Archive your full server or with only selected channel"
        )
@discord.app_commands.describe(archive_channel="update/add only a selected channel")
async def archive(interaction: discord.Interaction, archive_channel: discord.abc.GuildChannel = None):
    if (not user_authorized(interaction.guild, interaction.user)):
        await interaction.response.send_message("Seems like you are not authorized to do this. Ask the server owner to add a role that authorized, or to make one authorized.", ephemeral=True)
        return

    await interaction.response.send_message(f"Starting the export of {interaction.guild}...")

    guild = await client.fetch_guild(interaction.guild.id, with_counts=True)
    # by default with_counts is True, but set it just in case
    createDir(str(guild.id))
    createDir(str(guild.id)+"/assets/")
    createDir(str(guild.id)+"/attachments/")
    createDir(str(guild.id)+"/emojis")

    # TODO: channel re-export
    # this needs a check for an already existing export, import it, and then overwrite a given channel's export only
    
    text_channels = getChannelsList(guild.id, ctype="text")
    voice_channels = getChannelsList(guild.id, ctype="voice")
    channels_export = []

    if (archive_channel == None):
        print("----doing normal export")
        channels_export =  [await getTextChannelJSON(channel) for channel in text_channels]
        channels_export += [getVoiceChannelJSON(channel) for channel in voice_channels]
    else:
        # TODO: make these one-liners
        print(f"----doing changed export {archive_channel.name}")
        for tchannel in text_channels:
            if (tchannel.id == archive_channel.id):
                channels_export.append(await getTextChannelJSON(archive_channel))
        for vchannel in voice_channels:
            if (vchannel.id == archive_channel.id):
                channels_export.append(await getVoiceChannelJSON(archive_channel))


        if (len(channels_export) == 0): 
            await interaction.followup.send("Error occured with selecting this channel type: it is currently unsupported.", ephemeral=True)
        else:
            if ( not os.path.exists(str(guild.id)+"/core.json")):
                await interaction.followup.send("Warning: Couldn't find a full export before updating it partially.", ephemeral=True)
            else:
                with open(str(guild.id)+"/core.json", "r") as f:
                    exported = json.load(f)
                # update channels export to be the new one
                # new_channels_export = []
                old_channels = [e for e in exported["channels"] if e["id"] != archive_channel.id]
                print("DEBUG:", [e["name"] for e in old_channels])
                channels_export += old_channels
                # for e in exported["channels"]:
                #     print(f"keys: {e.keys()}")
                #     if e["id"] != archive_channel.id:
                #         new_channels_export.append(e)
                # new_channels_export.append(channels_export)
                # channels_export = new_channels_export


    # creating giant exported dictionary
    try:
        exported = {
                "export-info"                  : {
                    "end-date"                 : float(datetime.datetime.today().timestamp()),
                    "exporter-id"              : str(interaction.user.id)
                },
                "afk_timeout"                  : guild.afk_timeout,
                "approximate_member_count"     : guild.approximate_member_count,
                "approximate_presence_count"   : guild.approximate_presence_count,
                "premium_progress_bar_enabled" : guild.premium_progress_bar_enabled,
                "banner"                       : guild.banner,
                "bitrate_limit"                : guild.bitrate_limit,
                "created-at"                   : float(guild.created_at.timestamp()),
                "description"                  : guild.description,
                "discovery_splash"             : await getAssetJSON(guild.discovery_splash, str(guild.id)),
                "emoji_limit"                  : guild.emoji_limit,
                "features"                     : guild.features,
                "filesize_limit"               : guild.filesize_limit,
                "icon"                         : await getAssetJSON(guild.icon, str(guild.id)),
                "id"                           : str(guild.id),
                "large"                        : guild.large,
                "max_members"                  : guild.max_members,
                "max_presences"                : guild.max_presences,
                "max_video_channel_users"      : guild.max_video_channel_users,
                "member_count"                 : guild.member_count,
                "members"                      : [await getUserJSON(member, str(guild.id)) async for member in guild.fetch_members(limit=None)],
                "name"                         : guild.name,
                "mfa_level"                    : str(guild.mfa_level),
                "nsfw_level"                   : str(guild.nsfw_level),
                "owner_id"                     : guild.owner_id,
                "preferred_locale"             : str(guild.preferred_locale),
                "premium_progress_bar_enabled" : guild.premium_progress_bar_enabled,
                "premium_subscribers"          : [await getUserJSON(subscriber, str(guild.id)) for subscriber in guild.premium_subscribers],
                "premium_subscription_count"   : guild.premium_subscription_count, # don't ask why not take a len()
                "premium_tier"                 : guild.premium_tier,
                "splash"                       : await getAssetJSON(guild.splash, str(guild.id)),
                "sticker_limit"                : guild.sticker_limit,
                "system_channel_flags"         : guild.system_channel_flags.value,
                "unavailable"                  : guild.unavailable,
                "vanity_url"                   : guild.vanity_url,
                "vanity_url_code"              : guild.vanity_url_code,
                "verification_level"           : str(guild.verification_level),
                "widget_enabled"               : guild.widget_enabled,
                "audit_log"                    : [getAuditLogEntryJSON(entry) async for entry in guild.audit_logs(limit=None)],
                "emojis"                       : [await getEmojiJSON(emoji, str(guild.id)) for emoji in await guild.fetch_emojis()],

                # TODO emojis explicit_content_filter premium_subscriber_role public_updates_channel roles rules_channel scheduled_events stickers system_channel
                # TODO stage stuff

                # large ones
                "channels"                     : channels_export,
                "active-users"                 : users_json
        }
        

        # print(f"Exported a total of {total} messaegs")
        print("Done reading, writing to file...")
        with open(str(guild.id)+"/core.json", "w") as f:
            json.dump(exported, f)
        with open(str(guild.id)+"/core-pretty.json", "w") as f:
            json.dump(exported, f, indent=4)
    
        await interaction.followup.send("Done exporting!")
        print("Done!")
    except Exception as e:
        error_message = f"Error occured while exporting, on line {sys.exc_info()[2].tb_lineno}\n"
        error_message += str(e)
        await interaction.followup.send("Unexpected error occured whilst exporting. Try again in a few minutes.")
        # await interaction.followup.send(f"DEBUG: {error_message}")
        print("Exception in on_message")
        print(sys.exc_info()[2])

async def getTextChannelJSON(channel: discord.TextChannel) -> dict:
    print(f"Starting {channel}")
    c_pins = await channel.pins()
    messages = [message async for message in channel.history(limit=None)]
    total = len(messages)
    print(f"found {len(messages)} messages in {channel}")

    threads = channel.threads
    return ({
        "type"                          : "text",
        "name"                          : channel.name,
        "id"                            : str(channel.id),
        "category_id"                   : channel.category_id,
        "topic"                         : channel.topic,
        "position"                      : channel.position,
        "slowmode_delay"                : channel.slowmode_delay,
        "nsfw"                          : channel.nsfw,
        "default_auto_archive_duration" : channel.default_auto_archive_duration,
        "pins"                          : await getPinsJSON(await channel.pins()),
        "messages"                      : [await getMessageJSON(message) for message in messages],
        "threads"                       : [await getThreadJSON(thread) for thread in threads],
        "is_news"                       : channel.is_news(),
        "created_at"                    : float(channel.created_at.timestamp()),
        })

def getVoiceChannelJSON(channel: discord.VoiceChannel) -> dict:
    return ({
            "type"               : "voice",
            "bitrate"            : channel.bitrate,
            "category_id"        : channel.category_id,
            "created_at"         : float(channel.created_at.timestamp()),
            "id"                 : str(channel.id),
            "name"               : channel.name,
            "nsfw"               : channel.nsfw,
            "position"           : channel.position,
            "rtc_region"         : channel.rtc_region,
            "user_limit"         : channel.user_limit,
            "video_quality_mode" : str(channel.video_quality_mode)
            })


def getChannelsList(gid: int, ctype: str = "text") -> list:
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
    channel_list = []
    for channel in client.get_guild(gid).channels:
        if str(channel.type) == ctype:
            channel_list.append(channel)

    return channel_list 

async def getPinsJSON(messages: [discord.Message]) -> [int]:
    pin_ids = []
    for pin in messages:
        pin_ids.append(pin.id)
        
    return pin_ids

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
        users_json.append(await getUserJSON(message.author, str(message.guild.id)))

    return {
            "attachments" : [await getAttachmentJSON(attachment, str(message.guild.id)) for attachment in message.attachments],
            "author"      : str(message.author.id),
            "content"     : message.content,
            "created_at"  : str(float(message.created_at.timestamp())),
            "edited_at"   : getTimestampForReal(message.edited_at),
            "id"          : message.id,
            # TODO embed
            "flags"       : message.flags.value,
            "pinned"      : message.pinned,
            "reactions"   : [await getReactionJSON(reaction) for reaction in message.reactions ],
            "reference"   : getReferenceJSON(message.reference), 
            "stickers"    : [sticker.url for sticker in message.stickers],
            "type"        : str(message.type),
            "system_content" : message.system_content
    }

async def getAttachmentJSON(attachment: discord.Attachment, savedir: str) -> dict:
    """Returns a JSON serializable dictionary given an asset object.

    Returns and optionally saves the passed in asset object of type
    discord.Attachment. It saves the asset if the "save-assets" option is set
    to True in the config, if it is, it will save to the directory specified
    by the "asset-save-path" config option.

    Args:
        asset: a Discord asset object of type discord.Attachment
        savedir: where to save the attachments if needed

    Returns:
        Returns a JSON serializable dictionary representation of the argument
    """

    if (attachment == None): return None # we might get a None object in
    filename = savedir + "/attachments/" + str(attachment.id) + "-" + attachment.filename

    if (config["save-assets"] and not os.path.exists(filename)):
        try:
            print(f"[DEBUG] downloading asset to filename {filename}")
            await attachment.save(filename)
            # use_cached only works after only a few minutes, only slows the download down
        except Exception as e:
            print("[DEBUG] failed saving asset")
            print(str(e))

    return {
            "id"           : str(attachment.id),
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

async def getAssetJSON(asset:discord.Attachment, savedir: str) -> dict:
    if (asset == None): return None # we might get a None object in
    filename = savedir + "/assets/" + asset.key + ".png" # discord serves pngs
    if (config["save-assets"] and not os.path.exists(filename)):
        try:
            print(f"[DEBUG] downloading asset to filename {filename}")
            await asset.save(filename)
            # use_cached only works after only a few minutes, only slows the download down
        except Exception as e:
            print("[DEBUG] failed saving asset")
            print(str(e))
    return {"key" : asset.key}

async def getUserJSON(author: discord.abc.User, savedir: str) -> dict:
    """Returns a JSON compatible dictionary given an author object.

    Makes a serializable dictionary given a discord.abc.User type object that 
    can be exported to JSON. The resulting dictionary is a valid representation
    of the given object. The method does not require a valid discord client
    running.

    Args:
        author: a valid discord.abc.User implementating object.
        savedir: where to save the attachments if needed

    Returns:
        Returns a JSON serializable dictionary.
    """
    return {
            "name"           : author.name,
            "id"             : author.id,
            "accent_color"   : str(author.accent_color),
            "avatar"         : await getAssetJSON(author.avatar, savedir), 
            "banner"         : await getAssetJSON(author.banner, savedir),
            "bot"            : author.bot,
            "color"          : str(author.color),
            "created_at"     : str(float(author.created_at.timestamp())),
            "default_avatar" : await getAssetJSON(author.default_avatar, savedir),
            "discriminator"  : author.discriminator,
            "display_avatar" : await getAssetJSON(author.display_avatar, savedir),
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
        "archive_timestamp"     : float(thread.archive_timestamp.timestamp()),
        "archived"              : thread.archived,
        "archiver_id"           : thread.archiver_id,
        "auto_archive_duration" : thread.auto_archive_duration,
        "created_at"            : float(thread.created_at.timestamp()),
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
        "messages"              : [getMessageJSON(message) async for message in thread.history(limit=None)]
    }

def getThreadMemberJSON(member: discord.ThreadMember) -> dict:
    return {
            "id"        : member.id,
            "joined_at" : float(member.joined_at.timestamp())
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
            "created_at" : float(entry.created_at.timestamp()),
            "category"   : str(entry.category),
            # will not implement entry.before and entry.after
    }

async def getEmojiJSON(emoji: discord.Emoji, savedir: str) -> dict:
    filename = savedir + "/emojis/" + str(emoji.id)
    # select appropriate extension
    if (emoji.animated):
        filename += ".gif"
    else:
        filename += ".png"

    if (config["save-assets"] and not os.path.exists(filename)):
        try:
            print(f"[DEBUG] downloading emoji to filename {filename}")
            await emoji.save(filename)
            # use_cached only works after only a few minutes, only slows the download down
        except Exception as e:
            print("[DEBUG] failed saving asset")
            print(str(e))

    return {
            "name" : emoji.name,
            "id"   : str(emoji.id),
            # require_colons is useless for export
            "animated" : emoji.animated,
            "managed"  : emoji.managed,
#            "user"       : emoji.user.id,
            "created_at" : float(emoji.created_at.timestamp()),
            "url"        : emoji.url,
            }

def createDir(name: str):
    """Create a directory if not present

    Create a directory if it's not present, if a file exists with the same name
    delete it and create the directory.

    Args:
        name: the path of the directory to be created

    Returns:
        No returns.
    """

    if (not os.path.isdir(name)):
        if (os.path.exists(name)):
            os.remove(name)
            # removing the file of the same name
        os.mkdir(name)

def getTimestampForReal(time: datetime.datetime) -> float:
    if( time != None ):
        return float(time.timestamp())
    return None

def sync_settings() -> dict:
    """Sync servers settings locally
        
    Sync server settings data to a local variable from the file.

    Args:
        No arguments needed.

    Returns:
        An updated settings dictionary containing keys of server ids and values of authorized role ids
    """
    settings = {}
    with open("settings.bin", "r") as f:
        for line in f.readlines():
            split = line[:-1].split(",")
            settings[int(split[0])] = [int(e) for e in split[1:]]
    print("synced with the following:", settings)
    return settings

def dump_settings(settings: dict):
    """Dumps the local settings to file

    This function dumps the local variable passed in as argument to the file "settings.bin".

    Args:
        settings: dictionary of server settings

    Returns:
        This function doesn't return anything.
    """
    with open("settings.bin", "w") as f:
        for server_id in settings.keys():
            f.write(str(server_id))
            if (len(settings[server_id]) > 0):
                f.write(",")
                f.write(",".join([str(e) for e in settings[server_id]]))
            f.write("\n")
 
if __name__ == "__main__":
    users = []
    users_json = []

    global settings
    settings = sync_settings()
    
    try:
        client.run(config["token"])
    except Exception as e:
        print("An exception has occured while logging in:")
        print("\t" + str(e))
