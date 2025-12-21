# Générateur de Factures Seiko Mod

Outil simple pour générer des factures professionnelles pour les montres Seiko modifiées.

## Prérequis

- Python 3.6 ou supérieur
- pip (gestionnaire de paquets Python)
- venv (inclus avec Python 3.3+)

## Installation

### Sur macOS
1. Ouvrez le Terminal (⌘ + Espace, tapez "Terminal")
2. Vérifiez que Python est installé :
   ```bash
   python3 --version
   ```
3. Clonez ou téléchargez ce dépôt
4. Accédez au dossier du projet :
   ```bash
   cd ~/CascadeProjects/facturation_seiko
   ```
5. Créez un environnement virtuel :
   ```bash
   python3 -m venv venv
   ```
6. Activez l'environnement virtuel :
   ```bash
   source venv/bin/activate
   ```
   Vous devriez voir `(venv)` apparaître au début de votre ligne de commande.
7. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

### Sur Windows
1. Appuyez sur ⊞ + R, tapez `cmd` et appuyez sur Entrée
2. Vérifiez que Python est installé :
   ```cmd
   python --version
   ```
3. Téléchargez et décompressez le dépôt
4. Dans l'explorateur Windows, faites un clic droit sur le dossier du projet
5. Sélectionnez "Ouvrir dans le terminal"
6. Créez un environnement virtuel :
   ```cmd
   python -m venv venv
   ```
7. Activez l'environnement virtuel :
   ```cmd
   .\venv\Scripts\activate
   ```
   Vous devriez voir `(venv)` apparaître au début de votre ligne de commande.
8. Installez les dépendances :
   ```cmd
   pip install -r requirements.txt
   ```

## Utilisation

### Sur macOS
```bash
# Se rendre dans le dossier du projet (si ce n'est pas déjà fait)
cd ~/CascadeProjects/facturation_seiko

# Activer l'environnement virtuel (à faire à chaque nouvelle session)
source venv/bin/activate

# Lancer le script
python facture_seiko.py
```

Pour quitter l'environnement virtuel quand vous avez terminé :
```bash
deactivate
```

### Sur Windows
```cmd
# Se rendre dans le dossier du projet (si ce n'est pas déjà fait)
cd C:\chemin\vers\facturation_seiko

# Activer l'environnement virtuel (à faire à chaque nouvelle session)
.\venv\Scripts\activate

# Lancer le script
python facture_seiko.py
```

Pour quitter l'environnement virtuel quand vous avez terminé :
```cmd
deactivate
```

## Fonctionnalités

- Saisie des informations client
- Ajout de plusieurs articles
- Génération de PDF professionnels
- Compatible macOS et Windows
- Calcul automatique des totaux (HT, TVA, TTC)
- Ouverture automatique du PDF après génération

## Bonnes pratiques

### Gestion des dépendances
Après avoir ajouté de nouvelles dépendances, mettez à jour le fichier requirements.txt :
```bash
pip freeze > requirements.txt
```

### Ignorer l'environnement virtuel
Le dossier `venv/` est déjà ajouté au fichier `.gitignore`. Ne le versionnez jamais dans git.

## Personnalisation

Vous pouvez modifier le fichier `facture_seiko.py` pour :
- Changer les informations de votre entreprise
- Modifier le taux de TVA
- Ajuster la mise en page de la facture

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt.
