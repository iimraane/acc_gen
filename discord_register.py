import asyncio
from playwright.async_api import async_playwright
import time
import pyautogui

class DiscordRegistration:
    def __init__(self, account_generator):
        self.account_generator = account_generator
        self.extension_path = "C:/Users/windos 10/Desktop/Discord/tools/acc_gen/extension"
        self.browser = None
        self.page = None

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
        pyautogui.click(708, 914)
        pyautogui.write(self.account_generator.get_birthdate().split()[0])
        
        time.sleep(0.01)
        pyautogui.click(902, 911)
        pyautogui.write(self.account_generator.get_birthdate().split()[1])
                        
        time.sleep(0.01)
        pyautogui.click(1126, 912)
        pyautogui.write(self.account_generator.get_birthdate().split()[2])
        
        # Cocher les conditions d'utilisation et soumettre le formulaire
        await self.page.click('label:has-text("J\'ai lu et accepté les Conditions d\'Utilisation")')
        await self.page.click('button:has-text("Continuer")')

        self.account_generator.save_to_file(email, password)

        await asyncio.sleep(15)

    async def launch_browser(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir="C:/Users/windos 10/Desktop/Discord/tools/acc_gen/extension/user_data",
                headless=False,
                args=[f"--disable-extensions-except={self.extension_path}", f"--load-extension={self.extension_path}", "--disable-blink-features=AutomationControlled", "--enable-automation", "--no-first-run", "--no-default-browser-check"]
            )
            return browser

    async def close_browser(self):
        if self.browser:
            await self.browser.close()