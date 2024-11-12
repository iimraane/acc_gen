import asyncio
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class AccountGenerator:
    def __init__(self):
        self.email_domain = "@gmail.com"
        
    def generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def generate_account(self):
        username = self.generate_random_string()
        email = username + self.email_domain
        password = self.generate_random_string(12)
        return email, password

class DiscordRegistration:
    def __init__(self, account_generator):
        self.account_generator = account_generator
        self.chrome_options = Options()
        # Configurations Chrome
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = None

    async def __aenter__(self):
        # Initialiser le driver Chrome
        print("Démarrage de Chrome...")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # Fermer le navigateur
        if self.driver:
            self.driver.quit()
        print("Chrome fermé.")

    async def register_account(self, email, password):
        try:
            print(f"Création du compte: {email}")
            
            # Ouvrir Discord
            self.driver.get('https://discord.com/register')
            await asyncio.sleep(2)

            # Attendre que la page soit chargée
            wait = WebDriverWait(self.driver, 10)
            
            # Remplir le formulaire
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.send_keys(email)
            
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.send_keys(email.split('@')[0])
            
            password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.send_keys(password)
            
            # Date de naissance (exemple: 01/01/1990)
            day = wait.until(EC.presence_of_element_located((By.ID, "react-select-2-input")))
            day.send_keys("01")
            
            month = wait.until(EC.presence_of_element_located((By.ID, "react-select-3-input")))
            month.send_keys("01")
            
            year = wait.until(EC.presence_of_element_located((By.ID, "react-select-4-input")))
            year.send_keys("1990")

            # Accepter les conditions
            checkbox = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "checkbox-1ix_J3")))
            checkbox.click()

            # Cliquer sur le bouton d'inscription
            submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "button-1cRKG6")))
            submit_button.click()

            # Attendre un peu pour la création du compte
            await asyncio.sleep(5)
            
            print(f"Compte créé avec succès: {email}")
            
            # Sauvegarder les identifiants dans un fichier
            with open('accounts.txt', 'a') as f:
                f.write(f"{email}:{password}\n")

        except Exception as e:
            print(f"Erreur lors de la création du compte: {str(e)}")

async def main():
    account_generator = AccountGenerator()
    async with DiscordRegistration(account_generator) as discord_register:
        for i in range(10):
            try:
                email, password = account_generator.generate_account()
                await discord_register.register_account(email, password)
                # Attente aléatoire entre chaque création pour éviter la détection
                await asyncio.sleep(random.uniform(2, 5))
            except Exception as e:
                print(f"Erreur lors de la création du compte {i+1}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())