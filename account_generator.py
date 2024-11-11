import random
import string
import datetime
from pathlib import Path

def generate_email():
    # Générer une chaîne aléatoire de 8 à 12 caractères pour le nom d'utilisateur
    length = random.randint(8, 12)
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

def generate_random_name():
    # Générer un nom aléatoire pour `global_name` et `username`
    length = random.randint(4, 14)
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def save_to_file(email, password, filename="accounts.txt"):
    accounts_dir = Path("accounts")
    accounts_dir.mkdir(exist_ok=True)
    
    with open(accounts_dir / filename, "a") as file:
        file.write(f"{email}:{password}\n")
    print(f"Enregistré dans {filename}: {email}:{password}")

def get_birthdate():
    # Générer une date de naissance aléatoire entre 1970 et 2005
    start_date = datetime.date(1970, 1, 1)
    end_date = datetime.date(2005, 12, 31)
    
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    
    return random_date.strftime("%d %B %Y")