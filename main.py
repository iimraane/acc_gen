import asyncio
from account_generator import AccountGenerator
from discord_register import DiscordRegistration

async def main():
    account_generator = AccountGenerator()
    discord_register = DiscordRegistration(account_generator)
    
    # Générer des comptes et les enregistrer
    for _ in range(10):
        email, password = account_generator.generate_account()
        discord_register.register_account(email, password)
        
    # Fermer le navigateur
    await discord_register.close_browser()

if __name__ == "__main__":
    asyncio.run(main())