# Dexportiti
## What this is
This is a Discord bot written in python3 that aims to export every available information about a given server. The code itself uses discord.py and *python>=3.10*. This is because while Discord might seem a solid foundation to store information on, it poses a singular point of failure that could disappear overnight. With that all the moments I've had over the course of years would be gone, and I cannot let that happen.

Currently the bot is capable of exporting channel information, messages, reactions, user information, threads, and more mostly unimportant stuff. There is also a WIP barebones HTML/CSS/JS webUI that aims to recreate the server and show the exported information in a more pleasant way.

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
}
```
Whereas:
- "token" is the bot token the code will try to use. If you have no Discord application and/or don't know what that would be, you should refer to [the Discord developer portal's Documentation](https://discord.com/developers/docs/intro).
- "archive-command" is the exact string that the bot will look for when it recieves a message
- "admin-required" is whether the message sender must be admin, in order to start archiving. If true, it is required, and vice-versa.
- "save-assets" is whether or not to download discord assets and attachments to a local folder

Upon archival the bot will first create directory structure that will look like the following
```text
<guild-id>
├── assets
└── attachments
```

## Local webUI
Currently there is a barebones webUI that parses the locally saved data and displays it in your browser.
### running the webUI
Any webserver that can serve documents and files from the root directory of this repository should serve, however for convinience the development is done with Python's SimpleHTTPServer. To run after the export, do
```console
python3 -m http.server 8080
```
The `8080` part is the port it will be running on, if it interferes with other locally running webservices, it can be replaced.

To visit the webpage hosting the archive, visit [http://localhost:8080](http://localhost:8080). Or alternativelly, the desired port number after the colons.

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
- [X] export of emojis/stickers
- [X] make the dates saved UNIX timestamps
- [ ] local web UI
  - [X] display server information/statistics
  - [ ] fetch list of locally accessible webservers
  - [ ] reconstruct server from save
  - [X] save and use CDN served content locally (attachments/avatars/icons/emojis/stickers)
- [ ] misc. utilities
    - [ ] convert exports to a proper database format
    - [ ] index chats and make statisitcs
    - [ ] 
