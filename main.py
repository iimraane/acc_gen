import logging
import random
import string
import time
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass
import json
from selenium import webdriver
from selenium import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Configuration du logging avec rotation des fichiers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Account:
    email: str
    password: str
    creation_date: datetime
    status: str
    error: Optional[str] = None

class AccountGenerator:
    def __init__(self, email_domain: str = "@gmail.com"):
        self.email_domain = email_domain
        self._ensure_directories()

    def _ensure_directories(self):
        """Crée les répertoires nécessaires s'ils n'existent pas."""
        Path("accounts").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

    def generate_secure_password(self, length: int = 16) -> str:
        """Génère un mot de passe sécurisé avec des caractères variés."""
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special_chars = "!@#$%^&*"

        # Assure au moins un caractère de chaque type
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits),
            random.choice(special_chars)
        ]

        # Complète avec des caractères aléatoires
        all_chars = lowercase + uppercase + digits + special_chars
        password.extend(random.choices(all_chars, k=length-4))
        random.shuffle(password)
        return ''.join(password)

    def generate_account(self) -> Account:
        """Génère les informations d'un nouveau compte."""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        email = username + self.email_domain
        password = self.generate_secure_password()
        return Account(
            email=email,
            password=password,
            creation_date=datetime.now(),
            status="pending"
        )

class DiscordRegistration:
    def __init__(self, nopecha_key: str, headless: bool = False, proxy: str = None):
        self.nopecha_key = nopecha_key
        self.options = self._configure_chrome_options(headless, proxy)
        self._ensure_directories()

    def _ensure_directories(self):
        Path("accounts").mkdir(exist_ok=True)
        Path("extension").mkdir(exist_ok=True)

    def _configure_chrome_options(self, headless: bool, proxy: str = None) -> Options:
        """Configure les options de Chrome avec l'extension Nopecha."""
        options = Options()
        
        if headless:
            options.add_argument('--headless=new')

        # Configuration anti-détection
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        
        # User agent réaliste
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Ajout du proxy si spécifié
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')

        # Configuration de Nopecha
        options.add_argument('--load-extension=./extension/nopecha')
        
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        return options

    def _configure_nopecha(self, driver: webdriver.Chrome):
        """Configure l'extension Nopecha avec la clé API."""
        try:
            # Injection de la configuration Nopecha
            driver.execute_script(f"""
                localStorage.setItem('nopecha_key', '{self.nopecha_key}');
                localStorage.setItem('nopecha_auto', 'true');
            """)
        except Exception as e:
            logger.error(f"Erreur lors de la configuration de Nopecha: {str(e)}")

    def create_account(self, account: Account) -> bool:
        """Crée un compte Discord avec les informations fournies."""
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.options)
            wait = WebDriverWait(driver, 30)

            try:
                logger.info(f"Début de création du compte: {account.email}")
                driver.get('https://discord.com/register')
                self._configure_nopecha(driver)
                time.sleep(2)

                # Anti-détection
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                # Remplissage du formulaire
                self._fill_registration_form(driver, wait, account)

                # Vérification du succès
                success = self._verify_registration(driver, wait)
                if success:
                    account.status = "success"
                    self._save_account(account)
                    logger.info(f"Compte créé avec succès: {account.email}")
                else:
                    account.status = "failed"
                    account.error = "Échec de la vérification finale"
                    logger.warning(f"Échec de création du compte: {account.email}")

                return success

            except TimeoutException as e:
                account.status = "failed"
                account.error = f"Timeout: {str(e)}"
                logger.error(f"Timeout lors de la création du compte {account.email}: {str(e)}")
                return False
            except Exception as e:
                account.status = "failed"
                account.error = str(e)
                logger.error(f"Erreur lors de la création du compte {account.email}: {str(e)}")
                return False
            finally:
                driver.quit()
                self._save_account(account)

        except WebDriverException as e:
            account.status = "failed"
            account.error = f"Erreur WebDriver: {str(e)}"
            logger.error(f"Erreur WebDriver lors de la création du compte {account.email}: {str(e)}")
            return False

    def _fill_registration_form(self, driver: webdriver.Chrome, wait: WebDriverWait, account: Account):
        """Remplit le formulaire d'inscription."""
        # Email
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.send_keys(account.email)
        time.sleep(random.uniform(0.5, 1.5))

        # Username
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.clear()
        username_field.send_keys(account.email.split('@')[0])
        time.sleep(random.uniform(0.5, 1.5))

        # Password
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys(account.password)
        time.sleep(random.uniform(0.5, 1.5))

        # Date de naissance
        self._fill_birthday(driver, wait)

        # CGU
        self._accept_terms(driver, wait)

    def _fill_birthday(self, driver: webdriver.Chrome, wait: WebDriverWait):
        """Remplit la date de naissance de manière aléatoire."""
        # Jour
        day = wait.until(EC.presence_of_element_located((By.ID, "react-select-2-input")))
        day.send_keys(str(random.randint(1, 28)))
        day.send_keys(Keys.ENTER)
        time.sleep(random.uniform(0.5, 1.5))

        # Mois
        month = wait.until(EC.presence_of_element_located((By.ID, "react-select-3-input")))
        month.send_keys(str(random.randint(1, 12)))
        month.send_keys(Keys.ENTER)
        time.sleep(random.uniform(0.5, 1.5))

        # Année
        year = wait.until(EC.presence_of_element_located((By.ID, "react-select-4-input")))
        year.send_keys(str(random.randint(1990, 2000)))
        year.send_keys(Keys.ENTER)
        time.sleep(random.uniform(0.5, 1.5))

    def _accept_terms(self, driver: webdriver.Chrome, wait: WebDriverWait):
        """Accepte les conditions d'utilisation."""
        checkboxes = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "input[type='checkbox']")))
        if checkboxes:
            driver.execute_script("arguments[0].click(); arguments[0].checked = true;", checkboxes[-1])
        time.sleep(random.uniform(0.5, 1.5))

        # Clic sur le bouton de soumission
        submit_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[type='submit']")))
        driver.execute_script("arguments[0].click();", submit_button)
    
    def _solve_captcha(self, driver: webdriver.Chrome, wait: WebDriverWait, nopcha_key):
    
    
        endpoint = "https://api.nopecha.com/solve/hcaptcha"
        payload = {
            "key": nopcha_key,
            "site_key": site_key,
            "url": "https:discord.com/register"
        }

        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            result = response.json()

            if 'token' in result:
                return result['token']
            else:
                return f"Erreur: {result.get('error', 'Réponse inattendue')}"

        except requests.exceptions.RequestException as e:
            return f"Erreur de connexion: {e}"

    def _verify_registration(self, driver: webdriver.Chrome, wait: WebDriverWait) -> bool:
        """Vérifie si l'inscription a réussi."""
        try:
            time.sleep(10)  # Attente pour la résolution du captcha et le chargement
            return "/channels" in driver.current_url or "/app" in driver.current_url
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'inscription: {str(e)}")
            return False

    def _save_account(self, account: Account):
        """Sauvegarde les informations du compte."""
        # Sauvegarde dans le fichier texte
        with open('accounts/accounts.txt', 'a') as f:
            f.write(f"{account.creation_date} | {account.status} | {account.email}:{account.password}")
            if account.error:
                f.write(f" | Error: {account.error}")
            f.write("\n")

        # Sauvegarde au format JSON pour plus de détails
        account_data = {
            "email": account.email,
            "password": account.password,
            "creation_date": account.creation_date.isoformat(),
            "status": account.status,
            "error": account.error
        }
        
        json_file = Path("accounts/accounts.json")
        if json_file.exists():
            with open(json_file, 'r') as f:
                accounts = json.load(f)
        else:
            accounts = []
            
        accounts.append(account_data)
        with open(json_file, 'w') as f:
            json.dump(accounts, f, indent=4)

def main():
    try:
        # Configuration
        nopecha_key = input("Entrez votre clé API Nopecha: ")
        num_accounts = int(input("Combien de comptes voulez-vous créer ? "))
        use_proxy = input("Voulez-vous utiliser un proxy ? (o/n): ").lower() == 'o'
        proxy = input("Entrez l'adresse du proxy (format: ip:port): ") if use_proxy else None

        # Initialisation
        account_generator = AccountGenerator()
        discord_registration = DiscordRegistration(
            nopecha_key=nopecha_key,
            headless=False,  # Mode visible pour le débogage
            proxy=proxy
        )

        successful = 0
        for i in range(num_accounts):
            logger.info(f"Création du compte {i+1}/{num_accounts}")
            account = account_generator.generate_account()

            if discord_registration.create_account(account):
                successful += 1
                # Délai aléatoire entre les créations
                delay = random.uniform(30, 60)  # 30-60 secondes
                logger.info(f"Attente de {delay:.1f} secondes avant la prochaine création...")
                time.sleep(delay)

        logger.info(f"Création terminée. Comptes créés avec succès: {successful}/{num_accounts}")

    except KeyboardInterrupt:
        logger.info("\nArrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    main()