from __future__ import annotations

import re
import typing

from discord import Embed, Invite
from discord.errors import NotFound
from pydis_core.utils.regex import DISCORD_INVITE

import bot
from bot.exts.filtering._filter_context import Event, FilterContext
from bot.exts.filtering._filter_lists.filter_list import FilterList, ListType
from bot.exts.filtering._filters.filter import Filter
from bot.exts.filtering._filters.invite import InviteFilter
from bot.exts.filtering._settings import ActionSettings
from bot.exts.filtering._utils import clean_input

if typing.TYPE_CHECKING:
    from bot.exts.filtering.filtering import Filtering

# We tell the linter to ignore the long line lengths and print statements in this file.
# ruff: noqa: E501
# ruff: noqa: T201

REFINED_INVITE_CODE = re.compile(
    r"(?P<invite>[a-zA-Z0-9/_-]+)"  # The supposedly real invite code.
    r"(?:[^a-zA-Z0-9/].*)?"         # Ignoring anything that may come after an invalid character.
    r"$"                            # Up until the end of the string.
)


class InviteList(FilterList[InviteFilter]):
    """
    A list of filters, each looking for guild invites to a specific guild.

    If the invite is not whitelisted, it will be blocked. Partnered and verified servers are allowed unless blacklisted.

    Whitelist defaults dictate what happens when an invite is *not* explicitly allowed,
    and whitelist filters overrides have no effect.

    Blacklist defaults dictate what happens by default when an explicitly blocked invite is found.

    Items in the list are added through invites for the purpose of fetching the guild info.
    Items are stored as guild IDs, guild invites are *not* stored.
    """

    name = "invite"

    def __init__(self, filtering_cog: Filtering):
        super().__init__()
        filtering_cog.subscribe(self, Event.MESSAGE, Event.MESSAGE_EDIT, Event.SNEKBOX)

    def get_filter_type(self, content: str) -> type[Filter]:
        """Get a subclass of filter matching the filter list and the filter's content."""
        return InviteFilter

    @property
    def filter_types(self) -> set[type[Filter]]:
        """Return the types of filters used by this list."""
        return {InviteFilter}

    async def actions_for(
        self, ctx: FilterContext, flags: list[bool] = [False]*64,
    ) -> tuple[ActionSettings | None, list[str], dict[ListType, list[Filter]]]:
        """Dispatch the given event to the list's filters, and return actions to take and messages to relay to mods."""

        def cov_if(cond: int, index: int) -> bool:
            """
            Set the flag at the given index based on the condition.

            Expects condition and the index of the flag to set (increases linearly but creates two flags at index*2 and index*2+1 in the background).
            """
            if cond:
                flags[index*2] = True
            else:
                flags[index*2+1] = True
            return cond

        def cov_for(iterable: typing.Any, index: int) -> typing.Any:
            """
            Set the flag at the given index if the iterables have a length>0.

            Expects iterable and the index of the flag to set(increases linearly but creates two flags at index*2 and index*2+1 in the background).
            """
            if len(iterable) > 0:
                flags[index*2] = True
            else:
                flags[index*2+1] = True
            return iterable

        text = clean_input(ctx.content, keep_newlines=True)

        matches = list(DISCORD_INVITE.finditer(text))
        invite_codes = {m.group("invite") for m in cov_for(matches, 0)}
        if cov_if(not invite_codes, 1):
            return None, [], {}
        all_triggers = {}


        refined_invites = {}
        for invite_code in cov_for(invite_codes, 2):
            # Attempt to overcome an obfuscated invite.
            # If the result is incorrect, it won't make the whitelist more permissive or the blacklist stricter.
            refined_invite_code = invite_code
            if cov_if(match := REFINED_INVITE_CODE.search(invite_code), 3):
                refined_invite_code = match.group("invite")
            refined_invites[invite_code] = refined_invite_code


        _, failed = self[ListType.ALLOW].defaults.validations.evaluate(ctx)
        # If the allowed list doesn't operate in the context, unknown invites are allowed.
        check_if_allowed = not failed


        # Sort the invites into two categories:
        invites_for_inspection = dict()  # Found guild invites requiring further inspection.
        unknown_invites = dict()  # Either don't resolve or group DMs.
        for invite_code in cov_for(refined_invites.values(), 4):
            try:
                invite = await bot.instance.fetch_invite(invite_code)
            except NotFound:
                if cov_if(check_if_allowed, 5):
                    unknown_invites[invite_code] = None
            else:
                if cov_if(invite.guild, 6):  # Guild invite
                    invites_for_inspection[invite_code] = invite
                elif cov_if(check_if_allowed, 7):  # Group DM
                    unknown_invites[invite_code] = invite


        # Find any blocked invites
        new_ctx = ctx.replace(content={invite.guild.id for invite in cov_for(invites_for_inspection.values(), 8)})
        triggered = await self[ListType.DENY].filter_list_result(new_ctx)
        blocked_guilds = {filter_.content for filter_ in cov_for(triggered, 9)}
        blocked_invites = {
            code: invite for code, invite in cov_for(invites_for_inspection.items(), 10) if cov_if(invite.guild.id in blocked_guilds, 11)
        }


        # Remove the ones which are already confirmed as blocked, or otherwise ones which are partnered or verified.
        invites_for_inspection = {
            code: invite for code, invite in cov_for(invites_for_inspection.items(), 12)
            if cov_if(invite.guild.id not in blocked_guilds
            and "PARTNERED" not in invite.guild.features and "VERIFIED" not in invite.guild.features, 13)
        }

        # Remove any remaining invites which are allowed
        guilds_for_inspection = {invite.guild.id for invite in cov_for(invites_for_inspection.values(), 14)}


        if cov_if(check_if_allowed, 15):  # Whether unknown invites need to be checked.
            new_ctx = ctx.replace(content=guilds_for_inspection)
            all_triggers[ListType.ALLOW] = [
                filter_ for filter_ in cov_for(self[ListType.ALLOW].filters.values(), 16)
                if cov_if(await filter_.triggered_on(new_ctx), 17)
            ]

            allowed = {filter_.content for filter_ in cov_for(all_triggers[ListType.ALLOW], 18)}
            unknown_invites.update({
                code: invite for code, invite in cov_for(invites_for_inspection.items(), 19) if cov_if(invite.guild.id not in allowed, 20)
            })


        if cov_if(not triggered and not unknown_invites, 21):
            return None, [], all_triggers

        actions = None
        if cov_if(unknown_invites, 22):  # There are invites which weren't allowed but aren't explicitly blocked.
            actions = self[ListType.ALLOW].defaults.actions
        # Blocked invites come second so that their actions have preference.
        if cov_if(triggered, 23):
            if cov_if(actions, 24):
                actions = actions.union(self[ListType.DENY].merge_actions(triggered))
            else:
                actions = self[ListType.DENY].merge_actions(triggered)
            all_triggers[ListType.DENY] = triggered


        blocked_invites |= unknown_invites
        ctx.matches += {match[0] for match in cov_for(matches, 25) if cov_if(refined_invites.get(match.group("invite")) in blocked_invites, 26)}
        ctx.alert_embeds += (self._guild_embed(invite) for invite in cov_for(blocked_invites.values(), 27) if cov_if(invite, 28))
        if cov_if(unknown_invites, 29):
            ctx.potential_phish[self] = set(unknown_invites)

        messages = self[ListType.DENY].format_messages(triggered)
        messages += [
            f"`{code} - {invite.guild.id}`" if cov_if(invite, 30) else f"`{code}`" for code, invite in cov_for(unknown_invites.items(), 31)
        ]

        return actions, messages, all_triggers

    @staticmethod
    def _guild_embed(invite: Invite) -> Embed:
        """Return an embed representing the guild invites to."""
        embed = Embed()
        if invite.guild:
            embed.title = invite.guild.name
            embed.set_footer(text=f"Guild ID: {invite.guild.id}")
            if invite.guild.icon is not None:
                embed.set_thumbnail(url=invite.guild.icon.url)
        else:
            embed.title = "Group DM"

        embed.description = (
            f"**Invite Code:** {invite.code}\n"
            f"**Members:** {invite.approximate_member_count}\n"
            f"**Active:** {invite.approximate_presence_count}"
        )

        return embed
