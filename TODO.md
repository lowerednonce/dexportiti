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
- [ ] multi-server support
    - [X] handle archiving with interactions rather than a lazy "on\_message"
        - [X] optional argument for channel specification
    - [X] local guild settings
        - [X] allowed roles (list of roles)
    - [ ] upload it to some hosting option (IPFS or otherwise)
- [X] update export with channel

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
      - [X] autoformat URLs
      - [X] mentions
      - [ ] reactions
      - [X] replies
      - [X] edited status & date
      - [ ] stickers
      - [ ] emojis
  - [ ] threads
  - [ ] search
    - [X] HTML and JS around it
    - [X] plain text contents
    - [ ] regex contents
    - [ ] author
    - [ ] channel
    - [ ] before/after
        - [ ] warn if before is earlier than after
  - [X] server icon
  - [X] wipe previous HTML when selecting above
    - [X] wipe channel messages and channel info HTML when selecting a server
    - [X] wipe messages HTML when selecting a voice channel
  - [ ] all styling finished
- [ ] code formatting
    - [X] move to using `.` to access elements of imported data and not `[]`
    - [ ] format HTML inside of the javascript
        - [ ] indent
        - [ ] consistent line composition
- [ ] shift/port to another way to host a local web server easily

## Utilities

- [X] utility script to fix improper export to work better with JS
- [ ] convert exports to a proper database format
- [ ] index chats and make statistics

## testing

- [ ] multiple exports at once
- [ ] disk, network, CPU usage monitoring

## areas to revise

- [ ] if the guild export is doing its job properly
- [ ] continue work on updating exports/wider export management as there is buggy behaviour
- [ ] redo the webUI to be a multi-page application instead of trying to be an SPA
  - [ ] use GET arguments locally
