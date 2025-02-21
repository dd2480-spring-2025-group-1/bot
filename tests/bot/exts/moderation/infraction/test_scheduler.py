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
        # Basic mocks
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

        # Decouple dependencies by mocking them
        self.scheduler._pardon_action = AsyncMock(return_value={})

        mock_channel = AsyncMock()
        self.bot.get_channel.return_value = mock_channel

        self.bot.get_cog.return_value = AsyncMock()
        self.cog.apply_infraction = AsyncMock()
        self.cog.mod_log.ignore = Mock()
        self.ctx.guild.ban = AsyncMock()

        # Define a minimal infraction
        self.infraction_min = {
            "id": 123,
            "user": 456,
            "actor": 789,
            "type": "kick",
            "reason": "Test reason",
            "inserted_at": "2023-01-01T00:00:00Z",
            "expires_at": "2023-01-02T00:00:00Z",
            "active": True
        }

        @patch("bot.exts.moderation.infraction._utils.INFRACTION_ICONS", {"kick": ("some_url", "some_other_url")})
        async def test_deactivate_infraction_pardon_action_is_called(self):
            await self.scheduler.deactivate_infraction(self.infraction_min)

            # Ensure _pardon_action was called
            self.scheduler._pardon_action.assert_called_once_with(self.infraction_min, True)

        @patch("bot.exts.moderation.infraction._utils.INFRACTION_ICONS", {"kick": ("some_url", "some_other_url")})
        async def test_deactivate_infraction_logs_are_properly_written(self):
            logs = await self.scheduler.deactivate_infraction(self.infraction_min)

            self.assertIn("Member", logs)
            self.assertIn("Actor", logs)
            self.assertIn("Reason", logs)
            self.assertIn("Created", logs)

        @patch("bot.exts.moderation.infraction._utils.INFRACTION_ICONS", {"kick": ("some_url", "some_other_url")})
        async def test_deactivate_infraction_api_client_invoked(self):
            await self.scheduler.deactivate_infraction(self.infraction_min)
 
            # Ensure the infraction was marked as inactive in the database
            self.bot.api_client.patch.assert_called_once_with(
            f"bot/infractions/{infraction['id']}",
            f"bot/infractions/{self.infraction_min['id']}",
             json={"active": False}
         )

    @patch("bot.exts.moderation.infraction._utils.INFRACTION_ICONS", {"ban": ("some_url", "some_other_url")})
    async def test_deactivate_infraction_user_left_guild(self):
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

        log_text = await self.scheduler.deactivate_infraction(infraction)

        self.assertIn("Failure", log_text)
        self.assertEqual(log_text["Failure"], "User left the guild.")

        # Ensure _pardon_action was called
        self.scheduler._pardon_action.assert_called_once_with(infraction, True)

    @patch("bot.exts.moderation.infraction._utils.INFRACTION_ICONS", {"ban": ("some_url", "some_other_url")})
    async def test_deactivate_infraction_bot_lacks_permission(self):
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

        mock_forbidden = discord.Forbidden(
        response=Mock(status=403),
        message="Missing Permissions"
        )

        # Mock _pardon_action to return an exception
        self.scheduler._pardon_action = AsyncMock(side_effect=mock_forbidden)

        log_text = await self.scheduler.deactivate_infraction(infraction)

        self.assertIn("Failure", log_text)
        self.assertEqual(log_text["Failure"], "The bot lacks permissions to do this (role hierarchy?)")

        # Ensure _pardon_action was called
        self.scheduler._pardon_action.assert_called_once_with(infraction, True)

if __name__ == "__main__":
    unittest.main()
