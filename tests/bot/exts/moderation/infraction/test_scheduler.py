import os
import unittest
from unittest.mock import AsyncMock, Mock, patch
import discord

from dotenv import load_dotenv

from bot.exts.moderation.infraction._scheduler import InfractionScheduler
from bot.exts.moderation.infraction.infractions import Infractions
from tests.helpers import MockBot, MockContext, MockGuild, MockMember, MockRole

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "bot", ".env")

load_dotenv(dotenv_path)

class TestDeactivateInfractionMinimal(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.me = MockMember(id=7890, roles=[MockRole(id=7890, position=5)])
        self.bot = MockBot()
        self.cog = Infractions(self.bot)
        self.user = MockMember(id=1234, roles=[MockRole(id=3577, position=10)])
        self.target = MockMember(id=1265, roles=[MockRole(id=9876, position=1)])
        self.guild = MockGuild(id=4567)
        self.ctx = MockContext(me=self.me, bot=self.bot, author=self.user, guild=self.guild)


        # Initialize the InfractionScheduler with supported infractions
        self.scheduler = InfractionScheduler(self.bot, supported_infractions=[
            "ban", "kick", "timeout", "note", "warning", "voice_mute"
        ])

    @patch("bot.exts.moderation.infraction._utils.INFRACTION_ICONS", {"kick": ("some_url", "some_other_url")})
    async def test_deactivate_infraction_minimal(self):
        # Define a minimal infraction
        infraction = {
            "id": 123,
            "user": 456,
            "actor": 789,
            "type": "kick",
            "reason": "Test reason",
            "inserted_at": "2023-01-01T00:00:00Z",
            "expires_at": "2023-01-02T00:00:00Z",
            "active": True
        }

        # Mock _pardon_action to return a minimal log dictionary
        self.scheduler._pardon_action = AsyncMock(return_value={})

        # Mock the API client to succeed
        self.bot.api_client.patch = AsyncMock(return_value=None)

        mock_channel = AsyncMock()
        self.bot.get_channel.return_value = mock_channel

        self.cog.apply_infraction = AsyncMock()
        self.bot.get_cog.return_value = AsyncMock()
        self.cog.mod_log.ignore = Mock()
        self.ctx.guild.ban = AsyncMock()

        # Call the method under test
        log_text = await self.scheduler.deactivate_infraction(infraction)

        # Assertions to ensure the function was entered and basic behavior occurred
        self.assertIn("Member", log_text)
        self.assertIn("Actor", log_text)
        self.assertIn("Reason", log_text)
        self.assertIn("Created", log_text)

        # Ensure the infraction was marked as inactive in the database
        self.bot.api_client.patch.assert_called_once_with(
            f"bot/infractions/{infraction['id']}",
            json={"active": False}
        )

        # Ensure _pardon_action was called
        self.scheduler._pardon_action.assert_called_once_with(infraction, True)

    @patch("bot.exts.moderation.infraction._utils.INFRACTION_ICONS", {"ban": ("some_url", "some_other_url")})
    async def test_deactivate_infraction_user_left_guild(self):
        # Define a minimal infraction
        infraction = {
            "id": 456,
            "user": 789,
            "actor": 123,
            "type": "ban",
            "reason": "Test reason",
            "inserted_at": "2023-01-01T00:00:00Z",
            "expires_at": "2023-01-02T00:00:00Z",
            "active": True
        }

        mock_404 = discord.HTTPException(
        response=Mock(status=404),
        message="Not Found"
        )

        # Mock _pardon_action to return an exception
        self.scheduler._pardon_action = AsyncMock(side_effect=mock_404)

        # Mock the API client
        self.bot.api_client.patch = AsyncMock(return_value=None)

        mock_channel = AsyncMock()
        self.bot.get_channel.return_value = mock_channel

        self.cog.apply_infraction = AsyncMock()
        self.bot.get_cog.return_value = AsyncMock()
        self.cog.mod_log.ignore = Mock()
        self.ctx.guild.ban = AsyncMock()

        log_text = await self.scheduler.deactivate_infraction(infraction)

        self.assertIn("Failure", log_text)
        self.assertEqual(log_text["Failure"], "User left the guild.")

        # Ensure _pardon_action was called
        self.scheduler._pardon_action.assert_called_once_with(infraction, True)

if __name__ == "__main__":
    unittest.main()
