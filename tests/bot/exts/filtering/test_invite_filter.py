import unittest
from unittest.mock import MagicMock, patch

import arrow

from bot.exts.filtering._filter_context import Event, FilterContext
from bot.exts.filtering._filter_lists.filter_list import ListType
from bot.exts.filtering._filter_lists.invite import InviteList
from tests.helpers import MockBot, MockMember, MockMessage, MockTextChannel

BOT = MockBot()


class InviteListTests(unittest.IsolatedAsyncioTestCase):
    """Test the ExtensionsList class."""

    def setUp(self):
        """Sets up fresh objects for each test."""
        self.filter_list = InviteList(MagicMock())
        now = arrow.utcnow().timestamp()
        filters = []
        self.whitelist = ["120000000000000", "130000000000000", "140000000000000"]
        for i, filter_content in enumerate(self.whitelist, start=1):
            filters.append({
                "id": i, "content": filter_content, "description": None, "settings": {},
                "additional_settings": {}, "created_at": now, "updated_at": now
            })
        self.filter_list.add_list({
            "id": 1,
            "list_type": ListType.ALLOW,
            "created_at": now,
            "updated_at": now,
            "settings": {},
            "filters": filters
        })

        self.blacklist = ["122000000000000"]
        bfilters = []
        for i, filter_content in enumerate(self.blacklist, start=1):
            bfilters.append({
                "id": i, "content": filter_content, "description": None, "settings": {},
                "additional_settings": {}, "created_at": now, "updated_at": now
            })

        self.filter_list.add_list({
            "id": 2,
            "list_type": ListType.DENY,
            "created_at": now,
            "updated_at": now,
            "settings": {},
            "filters": bfilters
        })

        self.message = MockMessage()
        member = MockMember(id=123)
        channel = MockTextChannel(id=345)
        self.ctx = FilterContext(Event.MESSAGE, member, channel, "", self.message)

    @patch("bot.instance", BOT)
    async def test_no_invite_url(self):
        """Invite without url should return none."""
        ctx = self.ctx

        result = await self.filter_list.actions_for(ctx)

        self.assertEqual(result, (None, [], {}))

    @patch("bot.instance", BOT)
    async def test_valid_invite(self):
        """Invite with valid url should return message containg invite code."""
        content = "https://discord.gg/jmV5GEPt"
        ctx = self.ctx.replace(content=content)

        result = await self.filter_list.actions_for(ctx)
        self.assertEqual((result[0], result[2]), ({}, {ListType.ALLOW: []}))
        self.assertIn("jmV5GEPt", result[1][0])

    @patch("bot.instance", BOT)
    async def test_invalid_invite_url(self):
        """Invite with invalid url should return none."""
        content = "https://discor.g/jmV5GEPt"
        ctx = self.ctx.replace(content=content)

        result = await self.filter_list.actions_for(ctx)
        self.assertEqual((result[0], result[2]), (None, {}))

    @patch("bot.instance", BOT)
    async def test_valid_invite_with_different_url(self):
        """Invite with different, but valid url should return message containing the invite code."""
        content = "www.discord.me/jmV5GEPt"
        ctx = self.ctx.replace(content=content)

        result = await self.filter_list.actions_for(ctx)
        self.assertEqual((result[0], result[2]), ({}, {ListType.ALLOW: []}))
        self.assertIn("jmV5GEPt", result[1][0])
