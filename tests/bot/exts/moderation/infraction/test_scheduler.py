import unittest
from unittest.mock import AsyncMock, MagicMock

import bot
from bot.exts.moderation.infraction._scheduler import InfractionScheduler
from bot.exts.moderation.infraction.management import ModManagement
from tests.helpers import MockBot, MockContext, MockGuild, MockMember, MockMessage, MockRole


class ApplyInfractionTests(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.me = MockMember(id=7890, roles=[MockRole(id=7890, position=5)])

        self.bot = MockBot()
        mock_channel = MagicMock()
        mock_channel.send = AsyncMock(return_value=MockMessage())
        self.bot.get_channel = MagicMock(return_value=mock_channel)

        self.management_cog = ModManagement(self.bot)

        self.cog = InfractionScheduler(self.bot, supported_infractions=["ban", "mute", "warn"])
        self.user = MockMember(id=1234, roles=[MockRole(id=3577, position=10)])
        self.guild = MockGuild(id=4567)
        self.ctx = MockContext(me=self.me, bot=self.bot, author=self.user, guild=self.guild)

        bot.instance = self.bot

    async def test_apply_infraction_should_pass(self):

        user = MockMember(id=123456789)

        infraction = {
            "type": "ban",
            "reason": "Testing ban",
            "id": 1234,
            "jump_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "expires_at": "2023-01-02T00:00:00Z",
            "last_applied": "2023-01-02T00:00:00Z",
            "inserted_at": "2023-01-01T00:00:00Z",
            "hidden": False,
            "actor": 999,
            "user": user.id,
            "active": True
        }

        action = AsyncMock()

        results = await self.cog.apply_infraction(self.ctx, infraction, user, action=action)

        self.assertTrue(results)


    async def test_apply_infraction_wrong_type_should_fail(self):

        user = MockMember(id=123456789)

        infraction = {
            "type": "KILL",
            "reason": "Testing ban",
            "id": 1234,
            "jump_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "expires_at": "2023-01-02T00:00:00Z",
            "last_applied": "2023-01-02T00:00:00Z",
            "inserted_at": "2023-01-01T00:00:00Z",
            "hidden": False,
            "actor": 999,
            "user": user.id,
            "active": True
        }

        action = AsyncMock()

        with self.assertRaises(KeyError):
            await self.cog.apply_infraction(self.ctx, infraction, user, action=action)
