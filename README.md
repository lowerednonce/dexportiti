# Dexportiti
## What this is
This is a Discord bot written in python3 that aims to export every available information about a given server. The code itself uses discord.py and *python>=3.10*. This is because while Discord might seem a solid foundation to store information on, it poses a singular point of failure that could disappear overnight. With that all the moments I've had over the course of years would be gone, and I cannot let that happen

Currently the bot is capable of exporting channel information, messages, reactions, user information, and more mostly unimportant stuff. However, more is planned.

## Running locally
### installing requirements
To install the required python3 libraries run:
```console
pip3 install -r requirements.txt
```
So far, this is soley discord.py.
### running the bot
After that running the bot can be done by invoking:
```console
python3 main.py
```
However, the code expects a *config.json* file present, which consist of the following:
```json
{
  "token" : "BOT-TOKEN-GOES-HERE",
  "archive-command" : "ARCHIVING-COMMAND",
  "admin-required" : true/false,
  "save-assets" : true/false,
  "assets-save-path" : "DOWNLOADS-FOLDER"
}
```
Whereas:
- "token" is the bot token the code will try to use. If you have no Discord application and/or don't know what that would be, you should refer to [the Discord developer portal's Documentation](https://discord.com/developers/docs/intro).
- "archive-command" is the exact string that the bot will look for when it recieves a message
- "admin-required" is whether the message sender must be admin, in order to start archiving. If true, it is required, and vice-versa.
- "save-assets" is whether or not to download discord assets and attachments to a local folder
- "asset-save-path" is where to store the given downloaded files, if and only if "save-assets" is set to true. In that case the folder must exist, along with 2 sub-folders called "attachments" (for the message attachments) and "assets" (for the discord asssets, server icon, user profile pictures, emojis, etc)

## Planned
*Roughly in order of importance.*
### refactoring
- [X] moving from using a static guild id and export it on starting the bot, to an *$archive* command.
  - [X] refactor function signatures accordingly
- [X] add descriptions to all functions
- [X] rather than using `exported["key"] = value`, move to `exported = {"key": value, etc...}`
### features
- [X] export of threads
- [X] export of guild information (in progress)
- [X] export of non-text channels
- [ ] export of emojis/stickers
- [ ] make the dates saved UNIX timestamps
- [ ] local web UI
  - [ ] display server information/statistics
  - [ ] reconstruct server from save
  - [X] save and use CDN served content locally (attachments/avatars/icons/emojis/stickers)

* self-bot to download DMs/servers that you don't have admin access to? (this is a ToS infraction, ~and might require a significantly different approach~)
  * looked into it, it **does** violate the ToS, but it does not require that much code refactor.
