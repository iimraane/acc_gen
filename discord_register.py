import asyncio
from playwright.async_api import async_playwright
import time
import pyautogui
from account_generator import generate_email, generate_password, generate_random_name, save_to_file, get_birthdate

async def register_account():
    async with async_playwright() as p:
        extension_path = "C:/Users/windos 10/Desktop/Discord/tools/acc_gen/extension"
        
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="C:/Users/windos 10/Desktop/Discord/tools/acc_gen/extension/user_data",
            headless=False,
            args=[f"--disable-extensions-except={extension_path}", f"--load-extension={extension_path}", "--disable-blink-features=AutomationControlled", "--enable-automation", "--no-first-run", "--no-default-browser-check"]
        )

        page = await browser.new_page()
        
        await page.goto("https://discord.com/register")

        # Remplir le formulaire d'inscription
        email = generate_email()
        global_name = generate_random_name()
        username = generate_random_name()
        password = generate_password(15)
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="global_name"]', global_name)
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)

        # Sélectionner la date de naissance
        time.sleep(10)
        pyautogui.click(708, 914)
        pyautogui.write(get_birthdate().split()[0])
        
        time.sleep(0.01)
        pyautogui.click(902, 911)
        pyautogui.write(get_birthdate().split()[1])
                        
        time.sleep(0.01)
        pyautogui.click(1126, 912)
        pyautogui.write(get_birthdate().split()[2])
        
        # Cocher les conditions d'utilisation et soumettre le formulaire
        await page.click('label:has-text("J\'ai lu et accepté les Conditions d\'Utilisation")')
        await page.click('button:has-text("Continuer")')

        save_to_file(email, password)

        await asyncio.sleep(15)
        await browser.close()

asyncio.run(register_account())