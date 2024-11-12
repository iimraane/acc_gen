import asyncio
import logging
import random
import string
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AccountGenerator:
    def __init__(self):
        self.email_domain = "@gmail.com"
        
    def generate_secure_password(self, length: int = 16) -> str:
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = "!@#$%^&*"
        
        # Au moins un de chaque
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits),
            random.choice(special_chars)
        ]
        
        # Compléter avec des caractères aléatoires
        all_chars = lowercase + uppercase + digits + special_chars
        password.extend(random.choices(all_chars, k=length-4))
        random.shuffle(password)
        return ''.join(password)
    
    def generate_account(self) -> Tuple[str, str]:
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = username + self.email_domain
        password = self.generate_secure_password()
        return email, password

class DiscordRegistration:
    def __init__(self, headless: bool = False):
        self.options = Options()
        if headless:
            self.options.add_argument('--headless=new')
        
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Ajout de user-agent
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')

    def create_account(self, email: str, password: str) -> bool:
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.options)
            wait = WebDriverWait(driver, 15)
            
            try:
                # Accéder à la page d'inscription
                driver.get('https://discord.com/register')
                
                # Attendre que la page soit chargée
                email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
                
                # Remplir le formulaire
                email_field.send_keys(email)
                driver.find_element(By.NAME, "username").send_keys(email.split('@')[0])
                driver.find_element(By.NAME, "password").send_keys(password)
                
                # Date de naissance
                asyncio.sleep(1)
                day = wait.until(EC.presence_of_element_located((By.ID, "react-select-2-input")))
                day.send_keys(str(random.randint(1, 28)) + Keys.ENTER)
                
                month = wait.until(EC.presence_of_element_located((By.ID, "react-select-3-input")))
                month.send_keys(str(random.randint(1, 12)) + Keys.ENTER)
                
                year = wait.until(EC.presence_of_element_located((By.ID, "react-select-4-input")))
                year.send_keys(str(random.randint(1990, 2000)) + Keys.ENTER)
                
                # CGU
                checkboxes = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='checkbox']")))
                if checkboxes:
                    driver.execute_script("arguments[0].click();", checkboxes[-1])
                
                # Soumettre
                submit_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
                driver.execute_script("arguments[0].click();", submit_button)
                
                # Vérifier le résultat
                asyncio.sleep(5)
                if "/channels" in driver.current_url or "/app" in driver.current_url:
                    self._save_account(email, password)
                    logger.info(f"Compte créé avec succès: {email}")
                    return True
                else:
                    logger.warning(f"URL finale inattendue: {driver.current_url}")
                    return False
                    
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Erreur lors de la création du compte: {str(e)}")
            return False
            
    def _save_account(self, email: str, password: str):
        Path("accounts").mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('accounts/accounts.txt', 'a') as f:
            f.write(f"{timestamp} | {email}:{password}\n")

def main():
    try:
        num_accounts = int(input("Combien de comptes voulez-vous créer ? "))
        headless = input("Mode headless ? (o/n): ").lower() == 'o'
        
        account_generator = AccountGenerator()
        discord_registration = DiscordRegistration(headless=headless)
        
        successful = 0
        for i in range(num_accounts):
            logger.info(f"Création du compte {i+1}/{num_accounts}")
            email, password = account_generator.generate_account()
            
            if discord_registration.create_account(email, password):
                successful += 1
                
            # Délai entre les créations
            if i < num_accounts - 1:  # Ne pas attendre après le dernier compte
                delay = random.uniform(2, 4)
                logger.info(f"Attente de {delay:.1f} secondes avant la prochaine création")
                asyncio.sleep(delay)
        
        logger.info(f"\nCréation terminée. Comptes créés avec succès: {successful}/{num_accounts}")
        
    except KeyboardInterrupt:
        logger.info("\nArrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    main()