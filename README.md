# cogs

Custom cogs for [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot).

## Installation

Add this repository to your Red instance, then install a cog from it:

```
[p]repo add cogs https://github.com/poag/cogs
[p]cog install cogs <cogname>
[p]load <cogname>
```

## Cogs

| Cog | Description |
| --- | --- |
| `gamelog` | Logs what games members are playing per server, who's playing what, and how long each session lasts. Ignores non-game statuses (Spotify, custom statuses, etc). Requires the Presence and Server Members privileged intents. |
| `voicelog` | Logs who's in voice channels per server, and how long each session lasts. Requires the Voice States intent. |
| `autovoice` | Automatic voice channel creation: join a configured "source" voice channel and get moved into your own brand new voice channel, which is deleted once everyone leaves it. Requires the Voice States intent. Does *not* require the Presence or Server Members privileged intents for its core functionality - only the optional `game`-based room name/hint templates need the Presence intent (see below). Can migrate an existing AutoRoom setup with `[p]autovoiceset migrate`. |
| `timedroles` | Grants or removes roles based on how long a member has been on the server, with optional required-role gating and an announce channel for role changes. No privileged intents required. Can migrate an existing `timerole` setup with `[p]timedroles migrate`. |
| `auditlog` | Extended server event logging on top of Red's core modlog: message edits/deletes, member joins/leaves/updates, role/channel/thread create/update/delete, guild updates, emoji/sticker changes, voice state changes, bot command usage, and invite create/delete, each to a configurable channel as an embed or plain text. Requires the Server Members and Message Content privileged intents for full member-update and message-content logging; also needs the (non-privileged) Voice States, Invites, and Emojis and Stickers intents. Can migrate an existing ExtendedModLog setup with `[p]auditlog migrate`. |

### gamelog commands

| Command | Description |
| --- | --- |
| `[p]gamelog playtime [member]` | Total logged time per game for a member (yourself by default). |
| `[p]gamelog top <game>` | Top 10 players of a specific game, by time played. |
| `[p]gamelog leaderboard` | Top 10 players across all games combined, by time played. |
| `[p]gamelog games` | Every game logged in the server, sorted by total time played. |
| `[p]gamelog ignore <game>` | Bot owner only. Stop logging a game/app bot-wide (case-insensitive) - for non-game apps that use "Playing" rich presence. Pre-seeded with `YouTube Music`, `CurseForge`, `OVR Toolkit`. |
| `[p]gamelog unignore <game>` | Bot owner only. Resume logging a previously-ignored game/app. |
| `[p]gamelog ignored` | List games/apps currently ignored bot-wide. |

### voicelog commands

| Command | Description |
| --- | --- |
| `[p]voicelog voicetime [member]` | Total logged voice channel time per channel for a member (yourself by default). |

### autovoice commands

Member-facing, once you're in a room you own (alias `[p]av`):

| Command | Description |
| --- | --- |
| `[p]autovoice settings` (`about`, `info`) | Show your room's current settings. |
| `[p]autovoice name <name>` | Rename your room. |
| `[p]autovoice bitrate <kbps>` (`kbps`) | Change your room's bitrate. |
| `[p]autovoice users <user_limit>` (`userlimit`) | Change your room's user limit. |
| `[p]autovoice claim` | Claim ownership of a room whose owner has left. |
| `[p]autovoice public` | Make your room visible and joinable by everyone. |
| `[p]autovoice locked` | Make your room visible, but not joinable, by everyone. |
| `[p]autovoice private` | Hide your room from everyone. |
| `[p]autovoice allow <member_or_role>` (`add`) | Allow a member or role into your room. |
| `[p]autovoice deny <member_or_role>` (`ban`, `block`) | Deny (and disconnect) a member or role from your room. |

Admin-facing, for setting up sources (requires Manage Server):

| Command | Description |
| --- | --- |
| `[p]autovoiceset settings` | Show all AutoVoice Source settings for this server. |
| `[p]autovoiceset permissions` (`perms`) | Check the bot has the permissions each AutoVoice Source needs. |
| `[p]autovoiceset access admin` / `access mod` | Toggle whether admins/mods can join locked or private rooms. |
| `[p]autovoiceset access bot add/remove <role>` | Manage bot roles automatically allowed into every room. |
| `[p]autovoiceset create <source> <category>` (`enable`, `add`) | Set up a voice channel as an AutoVoice Source via a short setup wizard. |
| `[p]autovoiceset remove <source>` (`disable`, `delete`, `del`) | Remove an AutoVoice Source. |
| `[p]autovoiceset modify category <source> <category>` | Change a source's destination category. |
| `[p]autovoiceset modify type public/locked/private/server <source>` | Change the default room type a source creates. |
| `[p]autovoiceset modify name username/game/custom <source> [template]` | Change how created room names are generated. |
| `[p]autovoiceset modify hint set/disable <source> [text]` | Configure a welcome message sent into each new room's own chat. |
| `[p]autovoiceset modify specialperms ownermodify <source>` | Toggle whether room owners get Manage Channels on their room. |
| `[p]autovoiceset modify specialperms sendmessage <source>` | Toggle whether members can send messages in a room's own chat. |
| `[p]autovoiceset modify defaults` | Read how bitrate/user limit/permissions/member roles defaults work. |
| `[p]autovoiceset migrate` | One-time import of this server's AutoRoom setup - see [Migrating from AutoRoom](#migrating-from-autoroom) below. |

### timedroles commands

Admin-facing (requires being a mod/admin, or Manage Server via the mod-or-permissions check):

| Command | Description |
| --- | --- |
| `[p]timedroles addrole <role> <time> [requiredroles...]` | Grant `<role>` once a member has been on the server for `<time>` (e.g. `3d`, `1w2d`), optionally only once they already have one of `[requiredroles...]`. |
| `[p]timedroles removerole <role> <time> [requiredroles...]` | Same, but removes `<role>` instead of granting it. |
| `[p]timedroles channel [channel]` | Set (or clear, if omitted) the channel role grants/removals are announced to. |
| `[p]timedroles reapply` | Toggle re-granting a role if a member loses it some other way. Default on. |
| `[p]timedroles skipbots` | Toggle skipping bot accounts. Default on. |
| `[p]timedroles delrole <role>` | Stop tracking a role. |
| `[p]timedroles list` | List all currently configured timedroles. |
| `[p]timedroles migrate` | One-time import of this server's `timerole` setup - see [Migrating from timerole](#migrating-from-timerole) below. |
| `[p]runtimedroles` | Guild-owner only. Manually trigger the hourly check now, for troubleshooting. |

### auditlog commands

All `[p]auditlog` commands require Manage Server (or admin) permissions. `[events...]` accepts one or more event keys at once (e.g. `[p]auditlog toggle true message_edit message_delete`); a `member_`-prefixed key like `member_change` is accepted as an alias for the underlying `user_change` setting.

General settings (root `[p]auditlog`, aliases `[p]auditlogtoggle`/`[p]auditlogs`):

| Command | Description |
| --- | --- |
| `[p]auditlog settings` | Show every current setting for this server, pruning any stale ignored/per-event channel IDs along the way. |
| `[p]auditlog colour <colour> <events...>` (`color`) | Set a custom embed colour for one or more events. |
| `[p]auditlog embeds <true_or_false> <events...>` (`embed`) | Toggle embeds vs. plain text for one or more events. |
| `[p]auditlog emojiset <emoji> <events...>` | Set the emoji used in plain-text logs for one or more events. |
| `[p]auditlog toggle <true_or_false> <events...>` | Turn one or more events on or off. |
| `[p]auditlog channel <channel> <events...>` | Send one or more events to a specific channel, overriding the default modlog channel. |
| `[p]auditlog resetchannel <events...>` | Reset one or more events back to the default modlog channel. |
| `[p]auditlog all <true_or_false>` (`all_settings`, `toggle_all`) | Turn every event on or off at once. |
| `[p]auditlog commandlevel <levels...>` (`commandslevel`) | Set which command privilege levels (`NONE`/`MOD`/`ADMIN`/`GUILD_OWNER`/`BOT_OWNER`) get logged by `commands_used`. |
| `[p]auditlog migrate` | One-time import of this server's ExtendedModLog setup - see [Migrating from ExtendedModLog](#migrating-from-extendedmodlog) below. |

Message delete sub-settings (`[p]auditlog delete`):

| Command | Description |
| --- | --- |
| `[p]auditlog delete bulkdelete` | Toggle bulk message delete notifications. |
| `[p]auditlog delete individual` | Toggle also replaying each cached message from a bulk delete individually. |
| `[p]auditlog delete cachedonly` | Toggle delete notifications for messages the bot didn't have cached (channel info only, no content/author). |
| `[p]auditlog delete ignorecommands` | Toggle delete notifications for messages that were valid bot commands. |

Member-update sub-settings (`[p]auditlog member`, aliases `members`/`memberchanges`):

| Command | Description |
| --- | --- |
| `[p]auditlog member settings` | Show current member-update logging settings. |
| `[p]auditlog member nickname` (`nicknames`) | Toggle nickname changes. |
| `[p]auditlog member avatar` | Toggle guild-avatar changes. |
| `[p]auditlog member roles` (`role`) | Toggle role add/remove changes. |
| `[p]auditlog member pending` | Toggle membership-screening ("pending") changes. |
| `[p]auditlog member timeout` | Toggle timeout changes. |
| `[p]auditlog member flags` | Toggle member flag changes (`did_rejoin`, `completed_onboarding`, etc.). |
| `[p]auditlog member all <true_or_false>` | Set every member-update sub-setting at once. |

Ignore lists (`[p]auditlog ignore` / `[p]auditlog unignore`):

| Command | Description |
| --- | --- |
| `[p]auditlog ignore channel <channel>` / `unignore channel <channel>` | Ignore/unignore a channel (or category) from message delete/edit events and bot commands. |
| `[p]auditlog ignore user <user>` / `unignore user <user>` | Ignore/unignore a user from any event where they're the subject. |
| `[p]auditlog ignore mod <user>` / `unignore mod <user>` | Ignore/unignore a mod so events attributed to them (via the audit log) aren't logged. |

Bot-account filters (`[p]auditlog bot`, alias `bots`):

| Command | Description |
| --- | --- |
| `[p]auditlog bot edits` (`edit`) | Toggle message edit notifications for bot accounts. |
| `[p]auditlog bot deletes` (`delete`) | Toggle message delete notifications for bot accounts (cached messages only). |
| `[p]auditlog bot change` | Toggle bot accounts being logged in member-update events. |
| `[p]auditlog bot voice` | Toggle bot accounts being logged in voice state update events. |

### Migrating from timerole

`timedroles` is a from-scratch reimplementation of fox-v3's `timerole` cog. `[p]timedroles migrate` reads `timerole`'s own stored configuration directly and copies it into `timedroles`'s config for the current server - the announce channel, reapply/skipbots toggles, every configured role, and the per-member tracking state (whether they've already received a role, and when to next check them) so nobody gets a role re-granted or re-checked from scratch. Workflow:

1. `[p]unload timerole`.
2. `[p]load timedroles`.
3. In each server that used `timerole`, run `[p]timedroles migrate`. Safe to run more than once.
4. Confirm things work (`[p]runtimedroles` to trigger a check immediately), then `[p]unload timerole` for good (or `[p]cog uninstall` it) - `migrate` never does this for you.

### Migrating from AutoRoom

`autovoice` is a from-scratch reimplementation of PhasecoreX's `autoroom` cog (automatic voice channel creation), with the optional legacy companion text channel feature dropped - it's made obsolete by Discord's own voice channel text chat. `[p]autovoiceset migrate` reads AutoRoom's own stored configuration directly and copies it into `autovoice`'s config for the current server, so a bot owner can switch cogs without disrupting anything already set up. Workflow:

1. Make sure `autoroom` is loaded (so it has run its own internal migrations at least once), then `[p]unload autoroom` so the two cogs aren't both moving members around at the same time.
2. `[p]load autovoice`.
3. In each server that used AutoRoom, run `[p]autovoiceset migrate`. This copies over the server's admin/mod/bot access settings, every AutoRoom Source (minus its legacy text channel setting, which gets reported back to you as dropped if it was in use), and every currently open AutoRoom-created voice channel (so people keep their room ownership and deny lists without having to wait for the room to empty out). It's safe to run more than once.
4. Confirm things work by joining a source channel. Once you're happy, `[p]unload autoroom` for good (or `[p]cog uninstall` it) - `migrate` never does this for you.

### Migrating from ExtendedModLog

`auditlog` is a from-scratch reimplementation of TrustyJAID's `ExtendedModLog` cog, keeping the per-guild settings schema 1:1 (same event names, same sub-keys) so migration is a straight dict copy. `[p]auditlog migrate` reads ExtendedModLog's own stored configuration directly and copies it into `auditlog`'s config for the current server - every event's enabled/channel/colour/emoji/embed setting, the ignore lists, and the invite-uses snapshot used for join attribution. Workflow:

1. `[p]load auditlog` (ExtendedModLog can stay loaded for now - `migrate` only reads its config, it doesn't touch it).
2. In each server that used ExtendedModLog, run `[p]auditlog migrate`. It reports which events came out enabled, how many ignored channels/users/mods were carried over, and whether an invite snapshot came with them. Safe to run more than once.
3. Confirm things work (`[p]auditlog settings` to review, then trigger a couple of events), then `[p]unload extendedmodlog` for good (or `[p]cog uninstall` it) - `migrate` never does this for you, so both cogs will double-log events until you do.

A few behavioral differences from ExtendedModLog, all bug fixes rather than intentional feature changes:

- A custom `role_change` colour (`[p]auditlog colour`) now actually applies to role *updates*, not just role create/delete.
- `thread_delete`'s own embed toggle is respected (it used to silently read `channel_delete`'s instead).
- A member-flags-only change (e.g. `completed_onboarding`) is no longer silently dropped from logs.
- Attributing a join to an invite that got used up no longer risks failing silently on invites with no configured use limit.
- `[p]auditlog member all` can no longer corrupt every other server's settings - unlike `[p]modlog member all` in the original, which had a latent bug that could alias one server's live settings to the same shared defaults object used for every other server.
- `[p]auditlog all`'s `all_settings`/`toggle_all` aliases actually work (a typo meant the original's equivalents never registered).
- `[p]auditlog unignore channel` is symmetric with `[p]auditlog ignore channel` (the original's equivalent was only reachable as `unignore unignore_channel`).

### Relationship data

`gamelog` and `voicelog` each log plain `(guild, user, ..., start, end, duration)` session rows to their own SQLite database - `gamelog`'s `sessions` table (one row per game session) and `voicelog`'s `voice_sessions` table (one row per voice-channel session). Neither cog computes "who was with whom" or "what game were they playing while in voice" itself; both are derivable later by joining:

- `voicelog`'s `voice_sessions` against itself on matching `channel_id` with overlapping `[start_time, end_time]` windows, to find who shared a voice channel and for how long, and
- `voicelog`'s `voice_sessions` against `gamelog`'s `sessions` on matching `user_id` with overlapping time windows, to find what game (if any) someone was playing during a given voice session.

Since the two cogs keep separate database files (each in its own cog data folder), that second join needs both files open at once (e.g. SQLite's `ATTACH DATABASE`). Those joins are the intended basis for building a relationship graph from this data. `autovoice` doesn't fit into this - it doesn't log session history, only current live state (room ownership and deny lists).

## Privileged intents

`gamelog` needs the **Presence Intent** and **Server Members Intent** enabled for the bot, both in the [Discord developer portal](https://discord.com/developers/applications) (under your application's Bot settings) and in Red's own intents config (`redbot-setup` lets you toggle these, or edit the instance's intents). Without both, `gamelog` will never see game activity changes and will log nothing.

`voicelog` needs the **Voice States Intent**. It isn't a privileged intent, but Red's default intents config can still have it turned off - check the same intents settings as above.

`autovoice` also needs the **Voice States Intent** to see members joining/leaving voice channels at all - without it, it won't create or clean up rooms. It does *not* need the Server Members intent (member objects arrive attached to voice state updates regardless). It also does *not* need the Presence intent for its core room creation/deletion/ownership behavior. The one exception is the `game` channel-name/hint template variable (mirroring `gamelog`'s reliance on presence data): `discord.Member.activities` is only ever populated by presence data from Discord's gateway, which the client only receives (and caches) when the Presence intent is enabled - regardless of whether anything is listening for presence update events. So an AutoVoice Source configured with `[p]autovoiceset modify name game` will work without the Presence intent, but `{{game}}` will always render empty, and named rooms will just fall back to the username format.

`auditlog` needs two **privileged** intents to log everything it's meant to: the **Server Members Intent**, without which `on_member_join`/`on_member_remove`/`on_member_update` either don't fire at all or arrive without the data needed to log them (so `user_join`/`user_left`/`user_change` logging silently stops working); and the **Message Content Intent**, without which `message_edit`/`message_delete` events still fire, but the before/after message text is always empty (Discord replaces it with an empty string rather than omitting the field). It also needs the **Voice States**, **Invites**, and **Emojis and Stickers** intents for `voice_change`, `invite_created`/`invite_deleted` (and join-invite attribution), and `emoji_change`/`stickers_change` respectively - none of these three are privileged, but Red's intents config can still have them turned off, so check the same settings as above if those events aren't showing up. The **Presence Intent** is not used by this cog at all.

## Contact

Open an issue on this repository for bugs or feature requests.

## Credits

Built following the [Red-DiscordBot cog creation guide](https://docs.discord.red/en/stable/guide_cog_creation.html) and [publishing guide](https://docs.discord.red/en/stable/guide_publish_cogs.html).
