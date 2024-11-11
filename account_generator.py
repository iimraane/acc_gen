import asyncio
from playwright.async_api import async_playwright
import time
import pyautogui
import random
import string

def generate_email():
    # Générer une chaîne aléatoire de 8 à 12 caractères pour le nom d'utilisateur
    length = random.randint(12, 16)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    # Ajouter le domaine gmail.com
    email = f"{username}@gmail.com"
    
    return email

def generate_password(length=12):
    # Définir les types de caractères que le mot de passe doit inclure
    lower = string.ascii_lowercase  # Lettres minuscules
    upper = string.ascii_uppercase  # Lettres majuscules
    digits = string.digits           # Chiffres
    specials = string.punctuation    # Caractères spéciaux

    # S'assurer qu'il y a au moins un caractère de chaque type
    password = [
        random.choice(lower),  # Une minuscule
        random.choice(upper),  # Une majuscule
        random.choice(digits), # Un chiffre
        random.choice(specials) # Un caractère spécial
    ]

    # Ajouter des caractères aléatoires pour atteindre la longueur souhaitée
    all_chars = lower + upper + digits + specials
    password += random.choices(all_chars, k=length - 4)

    # Mélanger le mot de passe pour éviter un ordre prévisible
    random.shuffle(password)

    # Joindre les caractères en une seule chaîne
    return ''.join(password)

def save_to_file(email, password, filename="accounts.txt"):
            with open(filename, "a") as file:
                file.write(f"{email}:{password}\n")
            print(f"Enregistré dans {filename}: {email}:{password}")

def generate_random_name():
    # Générer un nom aléatoire pour `global_name` et `username`
    length = random.randint(4, 14)
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

async def main():
    async with async_playwright() as p:
        extension_path = "C:/Users/windos 10/Desktop/Discord/tools/acc_gen/extension"
        
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="C:/Users/windos 10/Desktop/Discord/tools/acc_gen/extension/user_data",
            headless=False,
            args=[f"--disable-extensions-except={extension_path}", f"--load-extension={extension_path}", "--disable-blink-features=AutomationControlled", "--enable-automation", "--no-first-run", "--no-default-browser-check"]
        )

        page = await browser.new_page()
        
        await page.goto("https://discord.com/register")

        # Remplir le nom d'affichage
        
        email = str(generate_email())
        global_name = str(generate_random_name())
        username = username()
        password = generate_password(15)
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="global_name"]', global_name)
        await page.fill('input[name="username"]', str(username))
        await page.fill('input[name="password"]', password)

        time.sleep(10)

        pyautogui.click(708, 914)
        random_number = random.randint(1, 30)
        pyautogui.write(str(random_number))
        
        time.sleep(0.01)

        pyautogui.click(902, 911)
        mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
        mois_choisi = random.choice(mois)
        pyautogui.write(mois_choisi)
                        
        time.sleep(0.01)

        pyautogui.click(1126, 912)
        random_date = random.randint(1970, 2005)
        pyautogui.write(str(random_date))
        
        await page.click('label:has-text("J\'ai lu et accepté les Conditions d\'Utilisation")')
        await page.click('button:has-text("Continuer")')

        save_to_file(email, password)

        await asyncio.sleep(15)
        await browser.close()

asyncio.run(main())
