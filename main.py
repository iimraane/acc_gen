import asyncio
from account_generator import AccountGenerator
from discord_register import DiscordRegistration
import os

async def main():
    account_generator = AccountGenerator()
    discord_register = DiscordRegistration(account_generator)

    async with discord_register:
        # Générer des comptes et les enregistrer
        for _ in range(10):
            email, password = account_generator.generate_account()
            discord_register.register_account(email, password)

if __name__ == "__main__":
    asyncio.run(main())