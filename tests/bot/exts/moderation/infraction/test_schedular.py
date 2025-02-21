import unittest
from unittest.mock import AsyncMock, patch

from bot.exts.moderation.infraction._scheduler import InfractionScheduler
from bot.exts.moderation.infraction.management import ModManagement
from tests.helpers import MockBot, MockContext, MockGuild, MockMember, MockRole


class ApplyInfractionTests(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.me = MockMember(id=7890, roles=[MockRole(id=7890, position=5)])
        self.bot = MockBot()

        self.management_cog = ModManagement(self.bot)

        self.cog = InfractionScheduler(self.bot, supported_infractions=["ban", "mute", "warn"])
        self.user = MockMember(id=1234, roles=[MockRole(id=3577, position=10)])
        self.guild = MockGuild(id=4567)
        self.ctx = MockContext(me=self.me, bot=self.bot, author=self.user, guild=self.guild)

    @patch("bot.exts.moderation.infraction._utils")
    @patch("bot.exts.moderation.infraction._utils.INFRACTION_ICONS", {"ban": ("some_url", "some_other_url")})
    async def test_apply_infraction(self, utils):

        user = MockMember(id=123456789)

        infraction = {
            "type" : "ban",
            "reason" : "Testing ban",
            "id" : 1234,
            "jump_url" : "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "expires_at" : "2023-01-02T00:00:00Z",
            "last_applied" : "2023-01-02T00:00:00Z",
            "inserted_at": "2023-01-01T00:00:00Z",
            "hidden" : False,
            "actor" : 999,
            "user" : user.id,
            "active" : True
        }

        action = AsyncMock()


        utils.notify_infraction = AsyncMock()

        result = await self.cog.apply_infraction(self.ctx, infraction, user, action=action)

        self.assertTrue(result)
        action.assert_awaited_once()
