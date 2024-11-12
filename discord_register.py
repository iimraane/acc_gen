import asyncio
from playwright.async_api import async_playwright
import time
import pyautogui
import os

class DiscordRegistration:
    def __init__(self, account_generator):
        self.account_generator = account_generator
        self.extension_path = os.path.join(os.path.dirname(__file__), "extension")
        self.browser = None
        self.page = None

    async def launch_browser(self):
        async with async_playwright() as p:
            user_data_dir = os.path.join(os.path.dirname(__file__), "extension", "user_data")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                args=[f"--disable-extensions-except={self.extension_path}", f"--load-extension={self.extension_path}", "--disable-blink-features=AutomationControlled", "--enable-automation", "--no-first-run", "--no-default-browser-check"]
            )
            return browser

    async def register_account(self, email, password):
        if not self.browser:
            self.browser = await self.launch_browser()
        self.page = await self.browser.new_page()
        
        await self.page.goto("https://discord.com/register")

        # Remplir le formulaire d'inscription
        await self.page.fill('input[name="email"]', email)
        await self.page.fill('input[name="global_name"]', self.account_generator.generate_random_name())
        await self.page.fill('input[name="username"]', self.account_generator.generate_random_name())
        await self.page.fill('input[name="password"]', password)

        # Sélectionner la date de naissance
        time.sleep(10)

        self.page.select_option('select#day', '5') # Sélection du mois 
        self.page.select_option('select#month', '1') # Sélection de l'année 
        self.page.select_option('select#year', '1990')

        # Cocher les conditions d'utilisation et soumettre le formulaire
        await self.page.click('label:has-text("J\'ai lu et accepté les Conditions d\'Utilisation")')
        await self.page.click('button:has-text("Continuer")')

        self.account_generator.save_to_file(email, password)

        await asyncio.sleep(15)


    async def close_browser(self):
        if self.browser:
            await self.browser.close()