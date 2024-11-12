import asyncio
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
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
        # Configuration améliorée de Chrome
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = None

    async def __aenter__(self):
        print("Démarrage de Chrome...")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        # Modifier les propriétés du navigator pour éviter la détection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()
        print("Chrome fermé.")

    def random_sleep(self, min_seconds=1, max_seconds=3):
        time.sleep(random.uniform(min_seconds, max_seconds))

    async def register_account(self, email, password):
        try:
            print(f"Création du compte: {email}")
            
            # Ouvrir Discord avec un user agent aléatoire
            self.driver.get('https://discord.com/register')
            self.random_sleep(2, 4)

            wait = WebDriverWait(self.driver, 15)
            
            # Remplir email avec simulation humaine
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            for char in email:
                email_field.send_keys(char)
                self.random_sleep(0.1, 0.3)

            # Remplir username
            username = email.split('@')[0]
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.clear()
            for char in username:
                username_field.send_keys(char)
                self.random_sleep(0.1, 0.2)

            # Remplir password
            password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            for char in password:
                password_field.send_keys(char)
                self.random_sleep(0.1, 0.3)

            # Date de naissance avec méthode améliorée
            try:
                # Sélectionner le mois (1-12)
                month_dropdown = wait.until(EC.presence_of_element_located((By.ID, "react-select-2-input")))
                month = str(random.randint(1, 12))
                month_dropdown.send_keys(month)
                month_dropdown.send_keys(Keys.ENTER)
                self.random_sleep()

                # Sélectionner le jour (1-28)
                day_dropdown = wait.until(EC.presence_of_element_located((By.ID, "react-select-3-input")))
                day = str(random.randint(1, 28))
                day_dropdown.send_keys(day)
                day_dropdown.send_keys(Keys.ENTER)
                self.random_sleep()

                # Sélectionner l'année (1990-2000)
                year_dropdown = wait.until(EC.presence_of_element_located((By.ID, "react-select-4-input")))
                year = str(random.randint(1990, 2000))
                year_dropdown.send_keys(year)
                year_dropdown.send_keys(Keys.ENTER)
                self.random_sleep()

            except Exception as e:
                print(f"Erreur avec la date: {str(e)}")
                # Méthode alternative pour la date
                try:
                    date_inputs = self.driver.find_elements(By.CSS_SELECTOR, "[class*='input-']")
                    if len(date_inputs) >= 3:
                        date_inputs[0].send_keys(month)
                        date_inputs[1].send_keys(day)
                        date_inputs[2].send_keys(year)
                except:
                    print("Erreur avec la méthode alternative de date")

            # Cocher la case des conditions avec JavaScript
            try:
                tos_checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='checkbox-']")))
                self.driver.execute_script("arguments[0].click();", tos_checkbox)
            except:
                print("Erreur avec la case à cocher des conditions")
                try:
                    # Méthode alternative
                    tos_checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox']")))
                    ActionChains(self.driver).move_to_element(tos_checkbox).click().perform()
                except:
                    print("Erreur avec la méthode alternative de case à cocher")

            self.random_sleep(1, 2)

            # Cliquer sur le bouton d'inscription
            try:
                submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[class*='button-']")))
                self.driver.execute_script("arguments[0].click();", submit_button)
            except:
                print("Erreur avec le bouton d'inscription")
                try:
                    # Méthode alternative
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    ActionChains(self.driver).move_to_element(submit_button).click().perform()
                except:
                    print("Erreur avec la méthode alternative de bouton")

            # Attendre la création du compte et vérifier le captcha si nécessaire
            await asyncio.sleep(5)
            
            # Vérifier si le compte a été créé avec succès
            if "discord.com/channels" in self.driver.current_url:
                print(f"Compte créé avec succès: {email}")
                with open('accounts.txt', 'a') as f:
                    f.write(f"{email}:{password}\n")
            else:
                print("Erreur possible lors de la création du compte")

        except Exception as e:
            print(f"Erreur lors de la création du compte: {str(e)}")

async def main():
    account_generator = AccountGenerator()
    async with DiscordRegistration(account_generator) as discord_register:
        for i in range(10):
            try:
                email, password = account_generator.generate_account()
                await discord_register.register_account(email, password)
                # Attente aléatoire entre chaque création
                await asyncio.sleep(random.uniform(3, 7))
            except Exception as e:
                print(f"Erreur lors de la création du compte {i+1}: {str(e)}")
                continue

if __name__ == "__main__":
    asyncio.run(main())