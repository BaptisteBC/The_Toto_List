import re

def evaluerMotDePasse(MDP):
    # Initialiser les critères
    longueurMotDePasse = len(MDP) >= 8
    critereMinuscule = bool(re.search(r'[a-z]', MDP))
    critereMajuscule = bool(re.search(r'[A-Z]', MDP))
    critereChiffre = bool(re.search(r'\d', MDP))
    critereCaractereSpecial = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', MDP))

    # Compter combien de critères sont respectés
    complexite = sum([longueurMotDePasse, critereMinuscule, critereMajuscule, critereChiffre, critereCaractereSpecial])

    # Déterminer le niveau de complexité
    if complexite == 5:
        return "Très sécurisé"
    elif complexite == 4:
        return "Sécurisé"
    elif complexite == 3:
        return "Moyennement sécurisé"
    elif complexite == 2:
        return "Faible"
    else:
        return "Très faible"

# Test du code
#MDP = input("Entrez un mot de passe : ")
#force = evaluerMotDePasse(MDP)
#print(f"La complexité du mot de passe est : {force}")
