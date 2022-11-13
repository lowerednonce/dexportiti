# Dexportiti
## What this is
This is a Discord bot written in python3 that aims to export every available information about a given server. The code itself uses discord.py and *python>=3.10*. This is because while Discord might seem a solid foundation to store information on, it poses a singular point of failure that could disappear overnight. With that all the moments I've had over the course of years would be gone, and I cannot let that happen

Currently the bot is capable of exporting channel information, messages, reactions, user information, and more mostly unimportant stuff. However, more is planned.

## Running locally
### installing requirements
Run
```bash
pip3 install -r requirements.txt
```
to install the required python3 packages, so far, this is soley discord.py.
### running the bot
If you want to run the bot locally, simply do
```bash
python3 main.py
```
However, the code expects a *config.json* file present, which should be the following
```json
{
  "token" : "BOT-TOKEN-GOES-HERE"
}
```
And it should store your discord bot's token. If you have no Discord application, you should refer to [fgh](asd)

## Planned
*Roughly in order of importance.*
### refactoring
- [ ] moving from using a static guild id and export it on starting the bot, to an *$archive* command.
  - [ ] refactor function signatures accordingly
- [ ] add descriptions to all functions
- [ ] rather than using `exported["key"] = value`, move to `exported = {"key": value, etc...}`
### features
- [ ] export of threads
- [ ] export of guild information
- [ ] export of non-text channels
- [ ] local web UI
  - [ ] display server information/statistics
  - [ ] reconstruct server
  - [ ] save and use CDN served content locally (attachments/avatars/icons/emojis/stickers)

* self-bot to download DMs/servers that you don't have admin access to? (this is a ToS infraction, and might require a significantly different approach)
