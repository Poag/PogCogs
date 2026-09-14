import asyncio
import datetime
import logging
import sqlite3
from typing import Dict, Optional, Tuple

import discord
from redbot.core import commands
from redbot.core.data_manager import cog_data_path
from redbot.core.utils.chat_formatting import humanize_timedelta

log = logging.getLogger("red.voicelog")


class VoiceLog(commands.Cog):
    """Logs who's in voice channels in a server, and how long each session lasts.

    Sessions are logged as plain start/end intervals per user per channel.
    This cog doesn't compute "who was with whom" itself - that's meant to
    be derived later by joining ``voice_sessions`` against itself on
    matching ``channel_id`` with overlapping ``[start_time, end_time]``
    windows. Cross-referencing against the ``gamelog`` cog's ``sessions``
    table (matching ``user_id``, overlapping time) shows what game someone
    was playing during a given voice session. Those joins are the intended
    basis for a relationship graph built from this data.

    Also opportunistically caches display names in ``user_names``,
    ``channel_names``, and ``guild_names`` - all three only ever store a
    Discord *ID*, so anything consuming this database directly (e.g. a
    dashboard) needs a name to show; refreshed from whichever
    member/channel/guild objects are already in hand on every voice
    state update rather than a separate lookup.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        db_path = cog_data_path(self) / "voicelog.sqlite3"
        self._db = sqlite3.connect(str(db_path), check_same_thread=False)
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS voice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                start_time INTEGER NOT NULL,
                end_time INTEGER NOT NULL,
                duration INTEGER NOT NULL
            )
            """
        )
        self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_voice_sessions_guild_user "
            "ON voice_sessions (guild_id, user_id)"
        )
        self._db.execute(
            "CREATE INDEX IF NOT EXISTS idx_voice_sessions_guild_channel_time "
            "ON voice_sessions (guild_id, channel_id, start_time, end_time)"
        )
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_names (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                updated_at INTEGER NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS channel_names (
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                updated_at INTEGER NOT NULL,
                PRIMARY KEY (guild_id, channel_id)
            )
            """
        )
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_names (
                guild_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                updated_at INTEGER NOT NULL
            )
            """
        )
        self._db.commit()
        self._db_lock = asyncio.Lock()
        # (guild_id, user_id) -> (channel_id, when that voice session started)
        self._active: Dict[Tuple[int, int], Tuple[int, datetime.datetime]] = {}

    def cog_unload(self) -> None:
        self._db.close()

    async def cog_load(self) -> None:
        if not self.bot.intents.voice_states:
            log.warning(
                "VoiceLog requires the Voice States intent to log voice channel "
                "activity. Enable it in Red's intents settings, then restart the bot."
            )
        asyncio.create_task(self._backfill_names())

    async def _backfill_names(self) -> None:
        """One-shot catch-up on load/reload.

        on_voice_state_update only ever refreshes a name when someone
        actually joins, leaves, or moves - so anyone who was already
        sitting in a channel before this cache existed (or before the
        most recent restart) would otherwise show a placeholder
        indefinitely, not just until their next real event. Backfilling
        from the current member/channel list on every load closes that
        gap immediately instead of waiting on activity.
        """
        await self.bot.wait_until_ready()
        now = int(discord.utils.utcnow().timestamp())
        user_rows = []
        channel_rows = []
        guild_rows = []
        for guild in self.bot.guilds:
            guild_rows.append((guild.id, guild.name, now))
            user_rows.extend(
                (guild.id, member.id, member.display_name, now)
                for member in guild.members
                if not member.bot
            )
            channel_rows.extend(
                (guild.id, channel.id, channel.name, now)
                for channel in (*guild.voice_channels, *guild.stage_channels)
            )
        if not user_rows and not channel_rows and not guild_rows:
            return

        def _upsert() -> None:
            self._db.executemany(
                "INSERT INTO user_names (guild_id, user_id, name, updated_at) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT (guild_id, user_id) DO UPDATE "
                "SET name = excluded.name, updated_at = excluded.updated_at",
                user_rows,
            )
            self._db.executemany(
                "INSERT INTO channel_names (guild_id, channel_id, name, updated_at) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT (guild_id, channel_id) DO UPDATE "
                "SET name = excluded.name, updated_at = excluded.updated_at",
                channel_rows,
            )
            self._db.executemany(
                "INSERT INTO guild_names (guild_id, name, updated_at) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT (guild_id) DO UPDATE "
                "SET name = excluded.name, updated_at = excluded.updated_at",
                guild_rows,
            )
            self._db.commit()

        async with self._db_lock:
            await asyncio.get_running_loop().run_in_executor(None, _upsert)
        log.info(
            f"VoiceLog: backfilled {len(user_rows)} member name(s), "
            f"{len(channel_rows)} channel name(s), and {len(guild_rows)} guild name(s)."
        )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ) -> None:
        if member.bot or before.channel == after.channel:
            return

        await self._touch_names(member, before.channel, after.channel)

        now = discord.utils.utcnow()
        key = (member.guild.id, member.id)

        if before.channel is not None:
            entry = self._active.pop(key, None)
            if entry is not None:
                channel_id, start = entry
                duration = int((now - start).total_seconds())
                if duration > 0:
                    await self._log_session(
                        member.guild.id, member.id, channel_id, start, now, duration
                    )

        if after.channel is not None:
            self._active[key] = (after.channel.id, now)

    async def _touch_names(self, member: discord.Member, *channels) -> None:
        now = int(discord.utils.utcnow().timestamp())
        channel_rows = [
            (member.guild.id, channel.id, channel.name, now)
            for channel in channels
            if channel is not None
        ]

        def _upsert() -> None:
            self._db.execute(
                "INSERT INTO user_names (guild_id, user_id, name, updated_at) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT (guild_id, user_id) DO UPDATE "
                "SET name = excluded.name, updated_at = excluded.updated_at",
                (member.guild.id, member.id, member.display_name, now),
            )
            self._db.executemany(
                "INSERT INTO channel_names (guild_id, channel_id, name, updated_at) "
                "VALUES (?, ?, ?, ?) "
                "ON CONFLICT (guild_id, channel_id) DO UPDATE "
                "SET name = excluded.name, updated_at = excluded.updated_at",
                channel_rows,
            )
            self._db.execute(
                "INSERT INTO guild_names (guild_id, name, updated_at) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT (guild_id) DO UPDATE "
                "SET name = excluded.name, updated_at = excluded.updated_at",
                (member.guild.id, member.guild.name, now),
            )
            self._db.commit()

        async with self._db_lock:
            await asyncio.get_running_loop().run_in_executor(None, _upsert)

    async def _log_session(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
        duration: int,
    ) -> None:
        def _insert() -> None:
            self._db.execute(
                "INSERT INTO voice_sessions "
                "(guild_id, user_id, channel_id, start_time, end_time, duration) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (guild_id, user_id, channel_id, int(start.timestamp()), int(end.timestamp()), duration),
            )
            self._db.commit()

        async with self._db_lock:
            await asyncio.get_running_loop().run_in_executor(None, _insert)

    @commands.guild_only()
    @commands.group()
    async def voicelog(self, ctx: commands.Context) -> None:
        """View logged voice channel activity for this server."""

    @voicelog.command(name="voicetime")
    async def voicelog_voicetime(
        self, ctx: commands.Context, member: Optional[discord.Member] = None
    ) -> None:
        """Show total logged voice channel time for a member (yourself by default)."""
        member = member or ctx.author

        def _query():
            cur = self._db.execute(
                "SELECT channel_id, SUM(duration) FROM voice_sessions "
                "WHERE guild_id = ? AND user_id = ? "
                "GROUP BY channel_id ORDER BY SUM(duration) DESC",
                (ctx.guild.id, member.id),
            )
            return cur.fetchall()

        async with self._db_lock:
            rows = await asyncio.get_running_loop().run_in_executor(None, _query)

        if not rows:
            await ctx.send(f"No logged voice activity for {member.display_name} in this server yet.")
            return

        lines = []
        for channel_id, total in rows:
            channel = ctx.guild.get_channel(channel_id)
            name = channel.name if channel else f"deleted-channel-{channel_id}"
            lines.append(f"#{name}: {humanize_timedelta(seconds=total)}")

        embed = discord.Embed(
            title=f"Voice time for {member.display_name}",
            description="\n".join(lines),
            color=await ctx.embed_color(),
        )
        await ctx.send(embed=embed)

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        def _delete() -> None:
            self._db.execute("DELETE FROM voice_sessions WHERE user_id = ?", (user_id,))
            self._db.execute("DELETE FROM user_names WHERE user_id = ?", (user_id,))
            self._db.commit()

        async with self._db_lock:
            await asyncio.get_running_loop().run_in_executor(None, _delete)
