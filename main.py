import asyncio
from account_generator import AccountGenerator
from discord_register import DiscordRegistration
import os

class DiscordRegistration:
    def __init__(self, account_generator):
        self.account_generator = account_generator

    async def __aenter__(self):
        # Initialiser les opérations d'enregistrement Discord
        print("Initialisation de l'enregistrement Discord")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # Effectuer les opérations de nettoyage lors de la sortie du gestionnaire de contexte
        print("Nettoyage de l'enregistrement Discord")

    async def register_account(self, email, password):
        # Effectuer l'enregistrement du compte Discord
        print(f"Enregistrement du compte Discord : {email}/{password}")
        await asyncio.sleep(1)  # Simule une opération asynchrone

async def main():
    account_generator = AccountGenerator()
    async with DiscordRegistration(account_generator) as discord_register:
        # Générer des comptes et les enregistrer
        for _ in range(10):
            email, password = account_generator.generate_account()
            await discord_register.register_account(email, password)

if __name__ == "__main__":
    asyncio.run(main())