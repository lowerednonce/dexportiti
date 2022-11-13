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
    # or if the message is "$archive" and is sent by the owner, continue
    if(not (message.content == "$archive")):
        return
    if (not (not config["admin-required"] or message.author.id == message.guild.owner_id)):
        # taking the admin-required config option into consideration
        return

    await message.reply(f"Starting the export of {message.guild}...")

    channels_export = []
    guild_id = message.guild.id
    channels = await getChannels(guild_id)
    efname = "export-" + str(guild_id)
    for channel in channels:
        messages = [message async for message in channel.history(limit=None)]
        channels_export.append({
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
    exported = {
            "guild_id" : guild_id,
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

async def getChannels(gid):
    text_channel_list = []
    for channel in client.get_guild(gid).channels:
        if str(channel.type) == 'text':
            text_channel_list.append(channel)

    return text_channel_list 

def getMessageJSON(message):
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

def getUserJSON(author):
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

def getMessageType(messageType):
    match messageType:
        case discord.MessageType.default: return "default"
        case discord.MessageType.recipient_add: return "recipient_add"
        case discord.MessageType.recipient_remove: return "recipient_remove"
        case discord.MessageType.call: return "call"
        case discord.MessageType.channel_name_change: return "channel_name_change"
        case discord.MessageType.channel_icon_change: return "channel_icon_change"
        case discord.MessageType.pins_add: return "pins_add"
        case discord.MessageType.new_member: return "new_member"
        case discord.MessageType.premium_guild_subscription: return "premium_guild_subscription"
        case discord.MessageType.premium_guild_tier_1: return "premium_guild_tier_1"
        case discord.MessageType.premium_guild_tier_2: return "premium_guild_tier_2"
        case discord.MessageType.premium_guild_tier_3: return "premium_guild_tier_3"
        case discord.MessageType.channel_follow_add: return "channel_follow_add"
        case discord.MessageType.guild_stream: return "guild_stream"
        case discord.MessageType.guild_discovery_disqualified: return "guild_discovery_disqualified"
        case discord.MessageType.guild_discovery_requalified: return "guild_discovery_requalified"
        case discord.MessageType.guild_discovery_grace_period_initial_warning: return "guild_discovery_grace_period_initial_warning"
        case discord.MessageType.guild_discovery_grace_period_final_warning: return "guild_discovery_grace_period_final_warning"
        case discord.MessageType.thread_created: return "thread_created"
        case discord.MessageType.reply: return "reply"
        case discord.MessageType.chat_input_command: return "chat_input_command"
        case discord.MessageType.guild_invite_reminder: return "guild_invite_reminder"
        case discord.MessageType.thread_starter_message: return "thread_starter_message"
        case discord.MessageType.context_menu_command: return "context_menu_command"
        case discord.MessageType.auto_moderation_action: return "auto_moderation_action"
        case _: return "undefined"

def getReactionJSON(reaction):
    return {
            "count" : reaction.count,
            "emoji" : str(reaction.emoji)
    }

def getReferenceJSON(reference):
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
