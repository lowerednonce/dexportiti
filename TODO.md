# TODO

## bot
- [X] moving from using a static guild id and export it on starting the bot, to an *$archive* command.
  - [X] refactor function signatures accordingly
- [X] add descriptions to all functions
- [X] rather than using `exported["key"] = value`, move to `exported = {"key": value, etc...}`
- [X] export of threads
- [X] export of guild information
- [X] export of non-text channels
- [X] export of emojis/stickers
- [X] make the dates saved UNIX timestamps
- [X] save and use CDN served content locally (attachments/avatars/icons/emojis/stickers)

## WebUI
- [X] display server information/statistics
- [X] fetch list of locally accessible web servers
- [ ] reconstruct server from save
  - [X] chat selection menu
  - [X] progressive loading of chat to prevent lag
  - [X] users
      - [X] profile picture
      - [X] name and discriminator
      - [X] id
      - [X] account creation date
      - [X] flags
  - [ ] messages
      - [X] content
      - [X] send date
      - [X] attachments
      - [X] sender pfp and name
      - [X] join messages
      - [X] pin status
      - [X] attachment display
          - [X] images
          - [X] videos
          - [ ] audio
          - [X] links to other file types
      - [ ] autoformat URLs
      - [ ] mentions
      - [ ] reactions
      - [ ] replies
      - [X] edited status & date
      - [ ] stickers
      - [ ] emojis
  - [ ] threads
  - [ ] all styling finished
- [ ] shift/port to another way to host a local web server easily

## Utilities

- [X] utility script to fix improper export to work better with JS
- [ ] convert exports to a proper database format
- [ ] index chats and make statistics
