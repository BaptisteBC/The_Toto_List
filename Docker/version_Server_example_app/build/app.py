from flask import Flask, jsonify
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration : chemin du répertoire à analyser
DIRECTORY_TO_HASH = os.environ['PROJECT_DEST'] #"/opt/toto_list"

# Vérification que le chemin est valide
def validate_directory(path):
    if not os.path.exists(path):
        raise ValueError(f"Le chemin {path} n'existe pas.")
    if not os.path.isdir(path):
        raise ValueError(f"Le chemin {path} n'est pas un répertoire.")

validate_directory(DIRECTORY_TO_HASH)

# Initialisation de l'application Flask
app = Flask(__name__)

@app.route("/version", methods=["GET"])
def version():
    try:
        # Commande shell pour calculer le hash global
        command = f"find {DIRECTORY_TO_HASH} -type f ! -path '*/.git/*' ! -path '*/__pycache__/*' -exec md5sum {{}} \\; " + "| awk '{print $1}' | sort | md5sum"
        result = subprocess.check_output(command, shell=True, text=True).strip()
        return result.split()[0]
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Erreur lors de l'exécution de la commande", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Une erreur inattendue s'est produite", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(port=80)
